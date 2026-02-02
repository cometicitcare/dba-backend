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
        
        # Fetch the user's role (required) and group (optional)
        user_role = db.query(Role).join(UserRole).filter(
            UserRole.ur_user_id == user.ua_user_id,
            UserRole.ur_is_active == True
        ).first()
        
        user_group = db.query(Group).join(UserGroup).filter(
            UserGroup.user_id == user.ua_user_id,
            UserGroup.is_active == True
        ).first()

        if not user_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
        
        # Group is optional - use "default" or None if no group assigned
        group_name = user_group.group_name if user_group else "default"
        
        # Create access and refresh tokens with role and group included
        access = self.create_access_token(user.ua_user_id, user_role.ro_role_name, group_name)
        refresh = self.create_refresh_token(user.ua_user_id)

        return access, refresh, user

    def create_access_token(self, user_id: str, role: str, group: str, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
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
    def initiate_password_reset(self, db: Session, identifier: str) -> tuple[bool, str, dict]:
        """
        Initiate password reset for a user given an identifier (email, username, or phone).

        Returns:
            (success: bool, message: str, payload: dict)
        payload contains: {"channels": {"email": bool, "sms": bool}, "user_id": str|None}
        """
        def _mask_email(email: str) -> str:
            try:
                local, domain = email.split("@", 1)
                if len(local) <= 2:
                    masked_local = local[0] + "*"
                else:
                    masked_local = local[0] + "***" + local[-1]
                return f"{masked_local}@{domain}"
            except Exception:
                return "***@***"

        def _mask_phone(phone: str) -> str:
            # keep last 3 digits, mask rest with *
            digits = "".join(ch for ch in phone if ch.isdigit())
            if len(digits) <= 3:
                return digits
            return "*" * (len(digits) - 3) + digits[-3:]

        GENERIC_MSG = "If an account exists you'll receive an OTP"

        try:
            # Try email
            user = db.query(UserAccount).filter(
                UserAccount.ua_email == identifier,
                UserAccount.ua_is_deleted == False,
            ).first()

            lookup_by = "email"
            if not user:
                # Try username
                user = db.query(UserAccount).filter(
                    UserAccount.ua_username == identifier,
                    UserAccount.ua_is_deleted == False,
                ).first()
                lookup_by = "username"

            if not user:
                # Try phone (normalize digits)
                digits = "".join(ch for ch in identifier if ch.isdigit())
                possible_phones = [identifier]
                if digits:
                    if digits.startswith("0"):
                        possible_phones.append("94" + digits[1:])
                    elif len(digits) == 9:
                        possible_phones.append("94" + digits)

                for p in possible_phones:
                    user = db.query(UserAccount).filter(
                        UserAccount.ua_phone == p,
                        UserAccount.ua_is_deleted == False,
                    ).first()
                    if user:
                        lookup_by = "phone"
                        break

            if not user:
                # No matching account — return generic message and empty payload
                return True, GENERIC_MSG, {"channels": {"email": False, "sms": False}, "user_id": None, "masked": None}

            # Found user — initiate password reset (email + optional SMS)
            success, _provider_msg, channels = password_reset_service.initiate_password_reset(
                user_id=user.ua_user_id,
                user_email=user.ua_email,
                user_name=user.ua_first_name or "User",
                user_phone=user.ua_phone,
            )

            logger.info(f"Password reset initiated for user: {user.ua_username} (by {lookup_by})")

            masked = {
                "email": _mask_email(user.ua_email) if user.ua_email else None,
                "phone": _mask_phone(user.ua_phone) if user.ua_phone else None,
            }

            # Always return generic message for safety, but include masked contact hints if available
            return True, GENERIC_MSG, {"channels": channels, "user_id": user.ua_user_id, "masked": masked}

        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return False, f"An error occurred: {str(e)}", {"channels": {"email": False, "sms": False}, "user_id": None}


    def validate_password_reset_otp(self, user_id: str, otp: str) -> tuple[bool, str]:
        """
        Validate OTP for password reset.

        Returns (is_valid, message)
        """
        try:
            is_valid, message = password_reset_service.validate_otp_for_reset(
                user_id=user_id,
                otp=otp,
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
        Complete password reset after OTP validation: update user's password and clear OTP.

        Returns (success, message)
        """
        try:
            user = db.query(UserAccount).filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted == False,
            ).first()

            if not user:
                logger.warning(f"Password reset attempt for non-existent user: {user_id}")
                return False, "User not found"

            from app.core.security import get_password_hash
            hashed_password = get_password_hash(new_password + user.ua_salt)

            user.ua_password_hash = hashed_password
            user.ua_must_change_password = False
            user.ua_password_expires = datetime.utcnow() + timedelta(days=90)
            user.ua_updated_at = datetime.utcnow()

            db.commit()

            # Clear OTP
            password_reset_service.complete_password_reset(user_id=user_id, new_password=new_password)

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

        Returns (success, message)
        """
        try:
            user = db.query(UserAccount).filter(
                UserAccount.ua_email == email,
                UserAccount.ua_is_deleted == False,
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
                    user_data=user_data,
                )

                if success:
                    logger.info(f"Username recovery email sent to: {email}")
                else:
                    logger.warning(f"Failed to send username recovery email to: {email}")

            # Return generic message for security
            return True, "If an account exists with this email, you will receive your username shortly."

        except Exception as e:
            logger.error(f"Error recovering username: {str(e)}")
            return True, "If an account exists with this email, you will receive your username shortly."

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
