import logging
import inspect

class UnifiedLogger:
    def __init__(self):
        # Configure single logger for entire application
        self.logger = logging.getLogger('DieselAutomation')
        
    def _get_caller_info(self):
        # Automatically detect calling file/function
        frame = inspect.currentframe().f_back.f_back
        filename = frame.f_code.co_filename.split('\\')[-1]  # Get just filename
        function = frame.f_code.co_name
        line_no = frame.f_lineno
        return f"{filename}:{function}:{line_no}"
    
    def info(self, message):
        source = self._get_caller_info()
        self.logger.info(f"{source} | {message}")
    
    def error(self, message):
        source = self._get_caller_info()
        self.logger.error(f"{source} | {message}")