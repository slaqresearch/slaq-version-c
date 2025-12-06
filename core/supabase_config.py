"""
Supabase configuration and client initialization.

This module provides server-side Supabase client initialization using
environment variables. The service role key should ONLY be used server-side
as it bypasses Row-Level Security (RLS).

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_ANON_KEY: Public anon key (for client-side safe operations)
    SUPABASE_SERVICE_ROLE_KEY: Service role key (server-side only, bypasses RLS)
"""

import os
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Lazy import to avoid hard dependency
_supabase_client = None
_supabase_admin_client = None


def _get_supabase_module():
    """Lazy import supabase module."""
    try:
        from supabase import create_client, Client
        return create_client, Client
    except ImportError:
        logger.warning(
            "supabase-py not installed. Install with: pip install supabase"
        )
        return None, None


@lru_cache(maxsize=1)
def get_supabase_config() -> dict:
    """
    Get Supabase configuration from Django settings.
    
    Returns:
        dict with url, anon_key, service_role_key, and bucket_name
    """
    try:
        from django.conf import settings
        return {
            'url': getattr(settings, 'SUPABASE_URL', ''),
            'anon_key': getattr(settings, 'SUPABASE_ANON_KEY', ''),
            'service_role_key': getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', ''),
            'bucket_name': getattr(settings, 'SUPABASE_BUCKET_NAME', 'audio-recordings'),
        }
    except Exception:
        # Fallback to environment variables
        return {
            'url': os.getenv('SUPABASE_URL', ''),
            'anon_key': os.getenv('SUPABASE_ANON_KEY', ''),
            'service_role_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''),
            'bucket_name': os.getenv('SUPABASE_BUCKET_NAME', 'audio-recordings'),
        }


def get_supabase_client(use_service_role: bool = False):
    """
    Get a Supabase client instance.
    
    Args:
        use_service_role: If True, use service role key (bypasses RLS).
                         Only use this for server-side admin operations.
    
    Returns:
        Supabase Client instance or None if not configured
    """
    global _supabase_client, _supabase_admin_client
    
    create_client, Client = _get_supabase_module()
    if create_client is None:
        return None
    
    config = get_supabase_config()
    
    if not config['url']:
        logger.warning("SUPABASE_URL not configured")
        return None
    
    if use_service_role:
        if not config['service_role_key']:
            logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured")
            return None
        
        if _supabase_admin_client is None:
            try:
                _supabase_admin_client = create_client(
                    config['url'],
                    config['service_role_key']
                )
                logger.info("Supabase admin client initialized")
            except Exception as e:
                logger.error(f"Failed to create Supabase admin client: {e}")
                return None
        return _supabase_admin_client
    else:
        if not config['anon_key']:
            logger.warning("SUPABASE_ANON_KEY not configured")
            return None
        
        if _supabase_client is None:
            try:
                _supabase_client = create_client(
                    config['url'],
                    config['anon_key']
                )
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {e}")
                return None
        return _supabase_client


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    config = get_supabase_config()
    return bool(config['url'] and (config['anon_key'] or config['service_role_key']))


def get_bucket_name() -> str:
    """Get the configured Supabase storage bucket name."""
    return get_supabase_config()['bucket_name']
