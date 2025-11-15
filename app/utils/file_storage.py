# app/utils/file_storage.py
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException


class FileStorageService:
    """
    Service for handling file uploads and storage.
    
    Files are stored in a structured directory:
    app/storage/<year>/<month>/<day>/<br_regn>/<filename>
    
    Industry best practices:
    - Store files on disk (not in database) for better performance
    - Use structured directory hierarchy for organization
    - Generate unique filenames to prevent conflicts
    - Return relative paths for database storage
    """
    
    def __init__(self, base_storage_path: str = "app/storage"):
        """
        Initialize the file storage service.
        
        Args:
            base_storage_path: Base directory for file storage
        """
        self.base_storage_path = Path(base_storage_path)
        
        # Ensure base directory exists
        self.base_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_storage_directory(self, br_regn: str) -> Path:
        """
        Generate the storage directory path based on current date and br_regn.
        
        Format: <base>/<year>/<month>/<day>/<br_regn>/
        
        Args:
            br_regn: Bhikku registration number
            
        Returns:
            Path object for the storage directory
        """
        now = datetime.utcnow()
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        
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
        
        # Validate extension (only allow images)
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
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
        file_type: str = "general"
    ) -> Tuple[str, str]:
        """
        Save an uploaded file to disk.
        
        Args:
            file: The uploaded file
            br_regn: Bhikku registration number
            file_type: Type of file (e.g., 'thumbprint', 'photo')
            
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
        
        # Generate storage directory
        storage_dir = self._get_storage_directory(br_regn)
        
        # Generate safe filename with type prefix
        original_filename = file.filename
        file_extension = Path(original_filename).suffix.lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        # Create filename with type prefix
        safe_filename = f"{file_type}_{timestamp}_{unique_id}{file_extension}"
        
        # Validate extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
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
