"""
Supabase Storage helpers for file upload/download operations.

This module provides utilities for interacting with Supabase Storage,
including signed URL generation for secure uploads and downloads.

Usage:
    from core.supabase_storage import upload_file, get_signed_url, delete_file
"""

import os
import logging
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, BinaryIO, Union
from datetime import timedelta

from .supabase_config import get_supabase_client, get_bucket_name, is_supabase_configured

logger = logging.getLogger(__name__)


def upload_file(
    file_path: Union[str, Path],
    remote_path: str,
    bucket_name: Optional[str] = None,
    content_type: Optional[str] = None,
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Upload a file to Supabase Storage.
    
    Args:
        file_path: Local path to the file to upload
        remote_path: Path in the bucket where file will be stored
        bucket_name: Storage bucket name (uses default if not specified)
        content_type: MIME type of the file (auto-detected if not specified)
        use_service_role: Use service role key for upload (recommended for server-side)
    
    Returns:
        Tuple of (success: bool, public_url or error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Auto-detect content type if not provided
    if content_type is None:
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or 'application/octet-stream'
    
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        response = client.storage.from_(bucket).upload(
            path=remote_path,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = client.storage.from_(bucket).get_public_url(remote_path)
        logger.info(f"Uploaded {file_path} to {bucket}/{remote_path}")
        return True, public_url
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def upload_file_object(
    file_obj: BinaryIO,
    remote_path: str,
    bucket_name: Optional[str] = None,
    content_type: str = 'application/octet-stream',
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Upload a file object (like Django's UploadedFile) to Supabase Storage.
    
    Args:
        file_obj: File-like object with read() method
        remote_path: Path in the bucket where file will be stored
        bucket_name: Storage bucket name (uses default if not specified)
        content_type: MIME type of the file
        use_service_role: Use service role key for upload
    
    Returns:
        Tuple of (success: bool, public_url or error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    
    try:
        file_data = file_obj.read()
        
        response = client.storage.from_(bucket).upload(
            path=remote_path,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        public_url = client.storage.from_(bucket).get_public_url(remote_path)
        logger.info(f"Uploaded file object to {bucket}/{remote_path}")
        return True, public_url
        
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_signed_url(
    remote_path: str,
    bucket_name: Optional[str] = None,
    expires_in: int = 3600,
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Generate a signed URL for secure file access.
    
    Args:
        remote_path: Path to the file in the bucket
        bucket_name: Storage bucket name (uses default if not specified)
        expires_in: URL expiration time in seconds (default: 1 hour)
        use_service_role: Use service role key
    
    Returns:
        Tuple of (success: bool, signed_url or error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    
    try:
        response = client.storage.from_(bucket).create_signed_url(
            path=remote_path,
            expires_in=expires_in
        )
        
        if response and 'signedURL' in response:
            return True, response['signedURL']
        elif response and 'signed_url' in response:
            return True, response['signed_url']
        else:
            return False, "Failed to generate signed URL"
            
    except Exception as e:
        error_msg = f"Signed URL generation failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_signed_upload_url(
    remote_path: str,
    bucket_name: Optional[str] = None,
    expires_in: int = 3600,
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Generate a signed URL for client-side upload.
    
    Args:
        remote_path: Path where the file will be stored
        bucket_name: Storage bucket name (uses default if not specified)
        expires_in: URL expiration time in seconds (default: 1 hour)
        use_service_role: Use service role key
    
    Returns:
        Tuple of (success: bool, signed_upload_url or error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    
    try:
        response = client.storage.from_(bucket).create_signed_upload_url(
            path=remote_path
        )
        
        if response and 'signedURL' in response:
            return True, response['signedURL']
        elif response and 'signed_url' in response:
            return True, response['signed_url']
        else:
            return False, "Failed to generate signed upload URL"
            
    except Exception as e:
        error_msg = f"Signed upload URL generation failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def download_file(
    remote_path: str,
    local_path: Union[str, Path],
    bucket_name: Optional[str] = None,
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Download a file from Supabase Storage.
    
    Args:
        remote_path: Path to the file in the bucket
        local_path: Local path where file will be saved
        bucket_name: Storage bucket name (uses default if not specified)
        use_service_role: Use service role key
    
    Returns:
        Tuple of (success: bool, local_path or error_message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    local_path = Path(local_path)
    
    try:
        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        response = client.storage.from_(bucket).download(remote_path)
        
        with open(local_path, 'wb') as f:
            f.write(response)
        
        logger.info(f"Downloaded {bucket}/{remote_path} to {local_path}")
        return True, str(local_path)
        
    except Exception as e:
        error_msg = f"Download failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def delete_file(
    remote_path: str,
    bucket_name: Optional[str] = None,
    use_service_role: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Delete a file from Supabase Storage.
    
    Args:
        remote_path: Path to the file in the bucket
        bucket_name: Storage bucket name (uses default if not specified)
        use_service_role: Use service role key
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not is_supabase_configured():
        return False, "Supabase not configured"
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, "Failed to get Supabase client"
    
    bucket = bucket_name or get_bucket_name()
    
    try:
        client.storage.from_(bucket).remove([remote_path])
        logger.info(f"Deleted {bucket}/{remote_path}")
        return True, f"Deleted {remote_path}"
        
    except Exception as e:
        error_msg = f"Delete failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def list_files(
    prefix: str = "",
    bucket_name: Optional[str] = None,
    use_service_role: bool = True
) -> Tuple[bool, list]:
    """
    List files in a Supabase Storage bucket.
    
    Args:
        prefix: Path prefix to filter files
        bucket_name: Storage bucket name (uses default if not specified)
        use_service_role: Use service role key
    
    Returns:
        Tuple of (success: bool, list of files or error_message)
    """
    if not is_supabase_configured():
        return False, ["Supabase not configured"]
    
    client = get_supabase_client(use_service_role=use_service_role)
    if client is None:
        return False, ["Failed to get Supabase client"]
    
    bucket = bucket_name or get_bucket_name()
    
    try:
        response = client.storage.from_(bucket).list(prefix)
        return True, response
        
    except Exception as e:
        error_msg = f"List failed: {str(e)}"
        logger.error(error_msg)
        return False, [error_msg]
