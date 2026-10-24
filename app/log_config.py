import logging
import os


def setup_logging():
    """
    Configures the root logger.
    Lambda already installs a handler on the root logger, so only add one
    when running locally. Level comes from LOG_LEVEL (default: DEBUG in dev,
    INFO otherwise).
    """
    is_dev = os.environ.get("ENV", "").lower() == "dev"
    level = os.environ.get("LOG_LEVEL", "DEBUG" if is_dev else "INFO").upper()

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
        )
    root.setLevel(level)

    # third-party libraries are too chatty at DEBUG
    for name in ("boto3", "botocore", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)
