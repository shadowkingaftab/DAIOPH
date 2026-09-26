#!/usr/bin/env python3
"""DAIOPH Edge service entry point."""

import logging
import os
import signal
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("daioph.edge")


def main():
    """Run the DAIOPH edge service."""
    logger.info("Starting DAIOPH Edge service...")

    # Set edge mode
    os.environ.setdefault("DAIOPH_MODE", "edge")

    # Import and start the application
    try:
        from APIs.rest.app import app

        import uvicorn

        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=int(os.environ.get("DAIOPH_PORT", "8000")),
            log_level="info",
        )
        server = uvicorn.Server(config)

        # Handle graceful shutdown
        def handle_shutdown(signum, frame):
            logger.info("Received shutdown signal, stopping...")
            server.should_exit = True

        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)

        logger.info("DAIOPH Edge service started on port %s", config.port)
        server.run()

    except ImportError as e:
        logger.error("Failed to import application: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Service error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()