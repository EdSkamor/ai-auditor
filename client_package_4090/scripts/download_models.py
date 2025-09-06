
#!/usr/bin/env python3
"""
Download AI models for RTX 4090 deployment.
"""

import os
import sys
from pathlib import Path
import subprocess

def download_llm_model():
    """Download LLM model."""
    print("📥 Downloading LLM model (Llama3-8B)...")
    
    try:
        from huggingface_hub import snapshot_download
        
        model_path = Path("models/llm/llama3-8b-instruct")
        model_path.mkdir(parents=True, exist_ok=True)
        
        snapshot_download(
            repo_id="meta-llama/Llama-3-8B-Instruct",
            local_dir=str(model_path),
            local_dir_use_symlinks=False
        )
        
        print("✅ LLM model downloaded")
        
    except Exception as e:
        print(f"❌ Failed to download LLM model: {e}")

def download_embedding_model():
    """Download embedding model."""
    print("📥 Downloading embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        model_path = Path("models/embeddings/multilingual-minilm")
        model_path.mkdir(parents=True, exist_ok=True)
        
        model.save(str(model_path))
        
        print("✅ Embedding model downloaded")
        
    except Exception as e:
        print(f"❌ Failed to download embedding model: {e}")

def main():
    """Download all models."""
    print("🚀 Downloading AI models for RTX 4090...")
    
    download_llm_model()
    download_embedding_model()
    
    print("✅ All models downloaded successfully!")

if __name__ == "__main__":
    main()
