
import logging
import sys
from typing import Any, Dict, Optional

def setup_logger(name: str = "scryptex", level: int = logging.INFO) -> logging.Logger:
    """Setup and return a logger instance"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_request(logger: logging.Logger, request_data: Dict[str, Any], user_id: Optional[str] = None) -> None:
    """Log an API request with user info if available"""
    log_data = {
        "request": request_data,
    }
    
    if user_id:
        log_data["user_id"] = user_id
        
    logger.info(f"API Request: {log_data}")
