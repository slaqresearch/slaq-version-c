"""
Download Wav2Vec2 Model for SLAQ

This script downloads the required AI model from Hugging Face.
Run this before deploying to production or for offline development.

Usage:
    python download_model.py

Requirements:
    - transformers
    - torch
    - internet connection
"""

import os
import sys
from pathlib import Path

def download_model():
    """Download Wav2Vec2 model from Hugging Face"""
    
    print("=" * 60)
    print("SLAQ AI Model Download")
    print("=" * 60)
    print()
    
    # Check if transformers is installed
    try:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        import torch
    except ImportError:
        print("❌ Error: Required packages not installed!")
        print()
        print("Please install required packages:")
        print("  pip install transformers torch")
        print()
        sys.exit(1)
    
    model_name = "facebook/wav2vec2-base-960h"
    
    print(f"📦 Model: {model_name}")
    print(f"📊 Expected Size: ~360 MB")
    print()
    print("⏳ Downloading model... (this may take 2-5 minutes)")
    print()
    
    try:
        # Download processor (tokenizer)
        print("1/2 Downloading processor...")
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        print("✅ Processor downloaded!")
        print()
        
        # Download model
        print("2/2 Downloading model weights...")
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        print("✅ Model downloaded!")
        print()
        
        # Verify model
        num_params = sum(p.numel() for p in model.parameters())
        print("=" * 60)
        print("✅ SUCCESS! Model downloaded and verified")
        print("=" * 60)
        print()
        print(f"📊 Model Info:")
        print(f"   - Name: {model_name}")
        print(f"   - Parameters: {num_params:,}")
        print(f"   - Status: Ready to use")
        print()
        
        # Show cache location
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        print(f"💾 Cache Location:")
        print(f"   {cache_dir}")
        print()
        print("🎉 You can now run SLAQ analysis without internet!")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR: Model download failed")
        print("=" * 60)
        print()
        print(f"Error details: {str(e)}")
        print()
        print("Possible solutions:")
        print("  1. Check your internet connection")
        print("  2. Try again (sometimes servers are busy)")
        print("  3. Use a VPN if Hugging Face is blocked")
        print("  4. Manually download from: https://huggingface.co/facebook/wav2vec2-base-960h")
        print()
        return False


def check_disk_space():
    """Check if there's enough disk space"""
    import shutil
    
    # Get home directory disk space
    home = Path.home()
    stat = shutil.disk_usage(home)
    
    free_gb = stat.free / (1024**3)
    
    print(f"💾 Available Disk Space: {free_gb:.2f} GB")
    
    if free_gb < 1:
        print("⚠️  Warning: Less than 1 GB free space")
        print("   Recommended: Free up at least 1 GB before downloading")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Download cancelled.")
            sys.exit(0)
    else:
        print("✅ Sufficient disk space available")
    
    print()


if __name__ == "__main__":
    print()
    
    # Check disk space
    try:
        check_disk_space()
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        print()
    
    # Download model
    success = download_model()
    
    # Exit code
    sys.exit(0 if success else 1)
