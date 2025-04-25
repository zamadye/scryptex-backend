
from datetime import datetime
from typing import Any, Dict
import uuid

def generate_response(data: Any = None, message: str = "OK", success: bool = True) -> Dict:
    """Generate a standardized API response"""
    return {
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    return f"{prefix}{uuid.uuid4().hex}"
