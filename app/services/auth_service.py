from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging

from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.models.group import Group
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.services.email_service import email_service
from app.services.password_reset_service import password_reset_service
from app.services.username_recovery_service import username_recovery_service

logger = logging.getLogger(__name__)

class AuthService:
    def authenticate(self, db: Session, username: str, password: str) -> tuple[str, str, UserAccount]:
        user = db.query(UserAccount).filter(
            UserAccount.ua_username == username,
            UserAccount.ua_is_deleted == False,
        ).first()

        # Passwords are stored as hash(plain_password + ua_salt)
        if not user or not verify_password(password + user.ua_salt, user.ua_password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Fetch the user's role and group information
        user_role = db.query(Role).join(UserRole).filter(UserRole.user_id == user.ua_user_id).first()
        user_group = db.query(Group).join(UserGroup).filter(UserGroup.user_id == user.ua_user_id).first()

        if not user_role or not user_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role or group not found")
        
        # Create access and refresh tokens with role and group included
        access = self.create_access_token(user.ua_user_id, user_role.ro_role_name, user_group.group_name)
        refresh = self.create_refresh_token(user.ua_user_id)

        return access, refresh, user

    def create_access_token(self, user_id: str, role: str, group: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
        to_encode = {
            "sub": user_id,
            "role": role,
            "group": group,
            "exp": datetime.utcnow() + expires_delta
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_jwt_token(user_id: str, role: str, group: str):
        expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "role": role,
            "group": group,
            "exp": expiration
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def create_refresh_token(self, user_id: str, expires_delta: timedelta = timedelta(days=7)) -> str:
        to_encode = {
            "sub": user_id,
            "exp": datetime.utcnow() + expires_delta
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return str(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # ============================================================================
    # EMAIL & PASSWORD RECOVERY METHODS
    # ============================================================================

    def initiate_password_reset(self, db: Session, email: str) -> tuple[bool, str]:
        """
        Initiate password reset for user.
        Finds user by email and sends OTP via email.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            tuple: (success, message)
        """
        try:
            user = db.query(UserAccount).filter(
                UserAccount.ua_email == email,
                UserAccount.ua_is_deleted == False
            ).first()

            if user:
                # Initiate password reset (generates OTP and sends email)
                success, message = password_reset_service.initiate_password_reset(
                    user_id=user.ua_user_id,
                    user_email=user.ua_email,
                    user_name=user.ua_first_name or "User",
                    user_phone=user.ua_phone,
                )

                if success:
                    logger.info(f"Password reset initiated for user: {user.ua_username}")
                else:
                    logger.warning(f"Failed to send password reset email to: {email}")
            else:
                logger.info(f"Password reset attempt for non-existent email: {email}")

            # Return generic message for security (prevent email enumeration)
            return (
                True,
                "If an account exists with this email, you will receive a password reset link shortly.",
            )

        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return (
                True,
                "If an account exists with this email, you will receive a password reset link shortly.",
            )

    def validate_password_reset_otp(self, user_id: str, otp: str) -> tuple[bool, str]:
        """
        Validate OTP for password reset.
        
        Args:
            user_id: User's ID
            otp: 6-digit OTP
            
        Returns:
            tuple: (is_valid, message)
        """
        try:
            is_valid, message = password_reset_service.validate_otp_for_reset(
                user_id=user_id,
                otp=otp
            )

            if is_valid:
                logger.info(f"OTP validated successfully for user: {user_id}")
            else:
                logger.warning(f"OTP validation failed for user: {user_id} - {message}")

            return is_valid, message

        except Exception as e:
            logger.error(f"Error validating OTP: {str(e)}")
            return False, "An error occurred during OTP validation"

    def complete_password_reset(self, db: Session, user_id: str, new_password: str) -> tuple[bool, str]:
        """
        Complete password reset after OTP validation.
        Updates user password and clears OTP.
        
        Args:
            db: Database session
            user_id: User's ID
            new_password: New password
            
        Returns:
            tuple: (success, message)
        """
        try:
            user = db.query(UserAccount).filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted == False
            ).first()

            if not user:
                logger.warning(f"Password reset attempt for non-existent user: {user_id}")
                return False, "User not found"

            # Hash the new password
            from app.core.security import get_password_hash
            hashed_password = get_password_hash(new_password + user.ua_salt)

            # Update password
            user.ua_password_hash = hashed_password
            user.ua_must_change_password = False
            user.ua_password_expires = datetime.utcnow() + timedelta(days=90)
            user.ua_updated_at = datetime.utcnow()

            db.commit()

            # Clear OTP
            password_reset_service.complete_password_reset(
                user_id=user_id,
                new_password=new_password
            )

            logger.info(f"Password reset completed for user: {user_id}")
            return True, "Password reset successful"

        except Exception as e:
            db.rollback()
            logger.error(f"Error completing password reset: {str(e)}")
            return False, f"Error completing password reset: {str(e)}"

    def recover_username(self, db: Session, email: str) -> tuple[bool, str]:
        """
        Recover username by email.
        Finds user by email and sends username recovery email.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            tuple: (success, message)
        """
        try:
            user = db.query(UserAccount).filter(
                UserAccount.ua_email == email,
                UserAccount.ua_is_deleted == False
            ).first()

            if user:
                user_data = {
                    "user_id": user.ua_user_id,
                    "username": user.ua_username,
                    "email": user.ua_email,
                    "first_name": user.ua_first_name or "User",
                    "status": user.ua_status or "active",
                }

                success, message = username_recovery_service.recover_username_by_email(
                    email=email,
                    user_data=user_data
                )

                if success:
                    logger.info(f"Username recovery email sent to: {email}")
                else:
                    logger.warning(f"Failed to send username recovery email to: {email}")
            else:
                logger.info(f"Username recovery attempt for non-existent email: {email}")

            # Return generic message for security (prevent email enumeration)
            return (
                True,
                "If an account exists with this email, you will receive your username shortly.",
            )

        except Exception as e:
            logger.error(f"Error recovering username: {str(e)}")
            return (
                True,
                "If an account exists with this email, you will receive your username shortly.",
            )

    def send_welcome_email(self, user: UserAccount, temporary_password: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            user: UserAccount object
            temporary_password: Temporary password for first login
            
        Returns:
            bool: Success status
        """
        try:
            html_content = email_service.load_template(
                "new_user",
                user_name=user.ua_first_name or user.ua_username,
                username=user.ua_username,
                temporary_password=temporary_password,
                email=user.ua_email,
                login_url=f"{settings.FRONTEND_URL}/login",
                support_url=f"{settings.FRONTEND_URL}/support",
                privacy_url=f"{settings.FRONTEND_URL}/privacy",
                terms_url=f"{settings.FRONTEND_URL}/terms",
            )

            success = email_service.send_email(
                to_email=user.ua_email,
                subject="Welcome to DBA HRMS - Your Account Has Been Created",
                html_content=html_content,
            )

            if success:
                logger.info(f"Welcome email sent to: {user.ua_email}")
            else:
                logger.warning(f"Failed to send welcome email to: {user.ua_email}")

            return success

        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False

# Create an instance of the AuthService
auth_service = AuthService()
