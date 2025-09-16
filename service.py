import signal
import sys
import os
import logging
import importlib.util
from serial_reader import start_serial_reading
from logger import UnifiedLogger

class DieselService:
    def __init__(self):
        self.logger = UnifiedLogger()
        self.running = True
        
        # Load external config if available
        self.load_external_config()
        
        # Configure logger if not already configured
        if not self.logger.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            self.logger.logger.setLevel(logging.INFO)
            self.logger.logger.addHandler(handler)
        
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
    def handle_shutdown(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def load_external_config(self):
        """Dynamically load config.py if it exists in the same directory as the executable"""
        try:
            # Get directory of the executable or script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                application_path = os.path.dirname(sys.executable)
            else:
                # Running as a script
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            config_path = os.path.join(application_path, 'config.py')
            
            if os.path.exists(config_path):
                self.logger.info(f"Loading external configuration from {config_path}")
                
                # Dynamically load the config module
                spec = importlib.util.spec_from_file_location("config", config_path)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # Update sys.modules to make the config available to other modules
                sys.modules["config"] = config_module
                self.logger.info("External configuration loaded successfully")
            else:
                self.logger.warning(f"External configuration file not found at {config_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading external configuration: {e}")
            
    def run(self):
        self.setup_signal_handlers()
        self.logger.info("Starting Diesel Automation Service")
        
        try:
            # Directly call your existing function
            start_serial_reading()
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            self.logger.info("Service shutting down")

if __name__ == "__main__":
    # This works for both development and as a service
    service = DieselService()
    service.run()