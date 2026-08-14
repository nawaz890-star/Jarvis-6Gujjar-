import signal
import sys
import logging
from core.app import CoreApp

logger = logging.getLogger(__name__)

def main():
    app = CoreApp()
    app.start()

    def signal_handler(sig, frame):
        logger.info("Received signal %s, shutting down.", sig)
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        # Keep running until interrupted
        logger.info("JARVIS Phase 1 running. Press Ctrl+C to stop.")
        while True:
            signal.pause()
    except AttributeError:
        # Windows: signal.pause may not exist; use a sleep loop
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler("KeyboardInterrupt", None)

if __name__ == "__main__":
    main()
