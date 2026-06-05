import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, 'extra_data'):
            log_record['data'] = record.extra_data
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger(name, log_file, level=logging.DEBUG, use_json=False):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding duplicate handlers if the logger is already configured
    if not logger.handlers:
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file), 
            maxBytes=5*1024*1024, 
            backupCount=3
        )
        file_handler.setLevel(level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO if use_json else logging.DEBUG)

        if use_json:
            file_handler.setFormatter(JSONFormatter())
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        else:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

class ObservabilityManager:
    def __init__(self):
        # We define specialized loggers for the AI observability system
        self.api_logger = setup_logger("api_logger", "api.log", logging.INFO, use_json=True)
        self.model_logger = setup_logger("model_logger", "models.log", logging.INFO, use_json=True)
        self.error_logger = setup_logger("error_logger", "errors.log", logging.ERROR, use_json=True)
        self.audit_logger = setup_logger("audit_logger", "audit.log", logging.INFO, use_json=True)

    def log_api_request(self, endpoint, method, response_time_ms, status_code):
        self.api_logger.info(f"API Request to {endpoint}", extra={'extra_data': {
            "endpoint": endpoint,
            "method": method,
            "response_time_ms": response_time_ms,
            "status_code": status_code
        }})

    def log_model_inference(self, model_name, candidate_id, output_score, latency_ms, metadata=None):
        data = {
            "model_name": model_name,
            "candidate_id": candidate_id,
            "output_score": output_score,
            "latency_ms": latency_ms
        }
        if metadata:
            data["metadata"] = metadata
            
        self.model_logger.info(f"Inference {model_name}", extra={'extra_data': data})

    def log_error(self, component, error_message, traceback_str=None):
        self.error_logger.error(f"Error in {component}: {error_message}", extra={'extra_data': {
            "component": component,
            "error_detail": error_message,
            "traceback": traceback_str
        }})

    def log_decision_audit(self, candidate_id, final_decision, confidence_score, mechanisms):
        self.audit_logger.info(f"Decision for {candidate_id}: {final_decision}", extra={'extra_data': {
            "candidate_id": candidate_id,
            "final_decision": final_decision,
            "confidence_score": confidence_score,
            "mechanisms": mechanisms
        }})

# Global observability instance
obs = ObservabilityManager()

def get_logger(name="ai_system"):
    """
    Initializes and returns a logger with rotating file handler and console handler.
    Maintained for backward compatibility.
    """
    return setup_logger(name, "extraction.log", logging.DEBUG, use_json=False)
