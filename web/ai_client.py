"""
AI Client for AI Auditor web interface.
Centralized HTTP client for AI API communication.
"""

from typing import Any, Dict, Optional
import time
import requests
from .config import AI_API_BASE, AI_TIMEOUT, AI_HEALTH


class AIClient:
    """Centralized AI API client with error handling and retries."""
    
    def __init__(self, base: str = AI_API_BASE, timeout: float = AI_TIMEOUT):
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AI-Auditor-Web/1.0"
        })
    
    def health(self) -> Dict[str, Any]:
        """Check AI API health status."""
        try:
            response = self.session.get(
                f"{self.base}{AI_HEALTH}", 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"AI API health check failed: {e}")
    
    def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send analysis request to AI API."""
        try:
            response = self.session.post(
                f"{self.base}/analyze", 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"AI API analysis failed: {e}")
    
    def analyze_file(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send file analysis request to AI API."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = options or {}
                response = self.session.post(
                    f"{self.base}/analyze-file", 
                    files=files,
                    data=data,
                    timeout=self.timeout * 2  # Longer timeout for file processing
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"AI API file analysis failed: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
    
    def wait_until_ready(self, retries: int = 10, delay: float = 1.0) -> bool:
        """Wait for AI API to be ready."""
        for attempt in range(retries):
            try:
                health_data = self.health()
                if (health_data.get("ready") or 
                    health_data.get("status") in {"ok", "healthy", "ready"}):
                    return True
            except Exception:
                if attempt < retries - 1:
                    time.sleep(delay)
        return False
    
    def is_online(self) -> bool:
        """Quick check if AI API is online."""
        try:
            self.health()
            return True
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed AI API status."""
        try:
            health_data = self.health()
            return {
                "online": True,
                "status": health_data.get("status", "unknown"),
                "ready": health_data.get("ready", False),
                "url": self.base,
                "timeout": self.timeout
            }
        except Exception as e:
            return {
                "online": False,
                "error": str(e),
                "url": self.base,
                "timeout": self.timeout
            }



