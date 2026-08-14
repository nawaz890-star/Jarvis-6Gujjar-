import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from core.config import Config
from config.logging_config import setup_logging

# Initialize logging first
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class CoreApp:
    def __init__(self):
        # Setup logging (already called above)
        self.logger = logging.getLogger("CoreApp")
        self.config = Config
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False

        # Ensure data directories exist
        data_dir = Path(self.config.DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("CoreApp initialized. Data directory: %s", data_dir)

        # Initialize long-term memory DB (if available)
        try:
            from memory.manager import LongTermMemory
            self.memory = LongTermMemory()
            self.logger.info("Long-term memory initialized at %s", self.memory.db_path)
        except Exception as e:
            self.memory = None
            self.logger.exception("Failed to initialize long-term memory: %s", e)

    def start(self):
        if self._running:
            self.logger.warning("CoreApp already running.")
            return
        self._running = True
        self.logger.info("Starting JARVIS Core.")
        # startup health checks
        self._startup_checks()

    def _startup_checks(self):
        # Check AI provider configuration — do not fail if missing; fallback will be used
        if not self.config.GEMINI_API_KEY or not self.config.GEMINI_API_URL:
            self.logger.warning("Gemini API not configured. AI provider set to local fallback.")
        else:
            self.logger.info("Gemini API configured (key not shown).")

    def stop(self):
        if not self._running:
            self.logger.warning("CoreApp not running.")
            return
        self.logger.info("Stopping JARVIS Core.")
        self.executor.shutdown(wait=True)
        self._running = False

    def submit_background(self, fn, *args, **kwargs):
        # Submit background work
        self.logger.debug("Submitting background task: %s", fn)
        return self.executor.submit(fn, *args, **kwargs)
