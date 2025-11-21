# app/utils/file_storage.py
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.core.config import settings


class FileStorageService:
    """
    Service for handling file uploads and storage.
    
    Files are stored in a structured directory:
    <storage_path>/<year>/<month>/<day>/<br_regn>/<filename>
    
    Industry best practices:
    - Store files on disk (not in database) for better performance
    - Use structured directory hierarchy for organization
    - Generate unique filenames to prevent conflicts
    - Return relative paths for database storage
    
    Railway Deployment:
    - Uses persistent volumes to prevent file loss on restarts
    - Storage path configurable via FILE_STORAGE_PATH environment variable
    """
    
    def __init__(self, base_storage_path: str = None):
        """
        Initialize the file storage service.
        
        Args:
            base_storage_path: Base directory for file storage (defaults to settings.FILE_STORAGE_PATH)
        """
        # Use provided path or fall back to settings, or default
        if base_storage_path is None:
            base_storage_path = getattr(settings, 'FILE_STORAGE_PATH', 'app/storage')
        
        self.base_storage_path = Path(base_storage_path)
        
        # Ensure base directory exists
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_storage_directory(self, br_regn: str, subdirectory: str = None) -> Path:
        """
        Generate the storage directory path based on current date and br_regn.
        
        Format: <base>/<subdirectory>/<year>/<month>/<day>/<br_regn>/
        or <base>/<year>/<month>/<day>/<br_regn>/ if subdirectory is None
        
        Args:
            br_regn: Bhikku registration number
            subdirectory: Optional subdirectory (e.g., 'bhikku_update', 'bhikku_id_card')
            
        Returns:
            Path object for the storage directory
        """
        now = datetime.utcnow()
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        
        if subdirectory:
            storage_dir = self.base_storage_path / subdirectory / year / month / day / br_regn
        else:
            storage_dir = self.base_storage_path / year / month / day / br_regn
        
        # Create directory if it doesn't exist
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        return storage_dir
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize and generate a safe filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename with unique identifier
        """
        # Get file extension
        file_extension = Path(filename).suffix.lower()
        
        # Validate extension (only allow images and PDFs)
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".pdf"}
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{unique_id}{file_extension}"
        
        return safe_filename
    
    async def save_file(
        self,
        file: UploadFile,
        br_regn: str,
        file_type: str = "general",
        subdirectory: str = None
    ) -> Tuple[str, str]:
        """
        Save an uploaded file to disk.
        
        Args:
            file: The uploaded file
            br_regn: Bhikku registration number
            file_type: Type of file (e.g., 'thumbprint', 'photo', 'scanned_document')
            subdirectory: Optional subdirectory (e.g., 'bhikku_update', 'bhikku_id_card')
            
        Returns:
            Tuple of (relative_path, absolute_path)
            
        Raises:
            HTTPException: If file validation fails or save fails
        """
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="File has no filename")
        
        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Reset file pointer
        await file.seek(0)
        
        # Generate storage directory with optional subdirectory
        storage_dir = self._get_storage_directory(br_regn, subdirectory)
        
        # Generate safe filename with type prefix
        original_filename = file.filename
        file_extension = Path(original_filename).suffix.lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        # Create filename with type prefix
        safe_filename = f"{file_type}_{timestamp}_{unique_id}{file_extension}"
        
        # Validate extension - support both images and PDFs
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".pdf"}
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Full path for saving
        file_path = storage_dir / safe_filename
        
        try:
            # Save file to disk
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Generate relative path for database storage
        relative_path = str(file_path.relative_to(self.base_storage_path))
        
        # Return both relative and absolute paths
        return f"/storage/{relative_path}", str(file_path)
    
    def delete_file(self, relative_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            relative_path: Relative path to the file (as stored in database)
            
        Returns:
            True if deleted, False if file not found
        """
        if not relative_path:
            return False
        
        # Remove leading /storage/ if present
        if relative_path.startswith("/storage/"):
            relative_path = relative_path[9:]  # Remove "/storage/"
        
        file_path = self.base_storage_path / relative_path
        
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
        except Exception:
            pass
        
        return False
    
    def rename_file(self, old_relative_path: str, new_relative_path: str) -> bool:
        """
        Rename/move a file from one path to another.
        
        Args:
            old_relative_path: Current relative path to the file (as stored in database)
            new_relative_path: New relative path for the file
            
        Returns:
            True if renamed successfully, False otherwise
            
        Raises:
            Exception: If renaming fails
        """
        if not old_relative_path or not new_relative_path:
            return False
        
        # Remove leading /storage/ if present
        if old_relative_path.startswith("/storage/"):
            old_relative_path = old_relative_path[9:]
        if new_relative_path.startswith("/storage/"):
            new_relative_path = new_relative_path[9:]
        
        old_file_path = self.base_storage_path / old_relative_path
        new_file_path = self.base_storage_path / new_relative_path
        
        try:
            if old_file_path.exists() and old_file_path.is_file():
                # Ensure the target directory exists
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                # Rename/move the file
                old_file_path.rename(new_file_path)
                return True
        except Exception as e:
            raise Exception(f"Failed to rename file from {old_relative_path} to {new_relative_path}: {str(e)}")
        
        return False
    
    def get_file_path(self, relative_path: str) -> Optional[Path]:
        """
        Get the absolute file path from a relative path.
        
        Args:
            relative_path: Relative path (as stored in database)
            
        Returns:
            Absolute Path object or None if file doesn't exist
        """
        if not relative_path:
            return None
        
        # Remove leading /storage/ if present
        if relative_path.startswith("/storage/"):
            relative_path = relative_path[9:]
        
        file_path = self.base_storage_path / relative_path
        
        if file_path.exists() and file_path.is_file():
            return file_path
        
        return None


# Singleton instance
file_storage_service = FileStorageService()
