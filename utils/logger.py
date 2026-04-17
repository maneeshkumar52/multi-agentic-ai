import logging
import sys

class Logger:
    _instances = {}

    def __new__(cls, name='MultiAgentPipeline'):
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, name='MultiAgentPipeline'):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        self.logger = logging.getLogger(name)
        if self.logger.handlers:
            return  # Already configured

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Set level
        self.logger.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_agent_activity(self, agent_name, action, details=None):
        """Log agent activity"""
        message = f"[{agent_name}] {action}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def log_error(self, message, exception=None):
        """Log error with optional exception details"""
        if exception:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)