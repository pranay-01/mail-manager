from handlers import start_processing
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


class SuppressFilter(logging.Filter):
    def filter(self, record):
        # suppressing DEBUG messages from googleapiclient.discovery and google_auth_httplib2
        if (record.levelno == logging.DEBUG or record.levelno == logging.WARNING) and (
                record.name.startswith("google")
        ):
            return False
        return True


logging.getLogger().handlers[-1].addFilter(SuppressFilter())


if __name__ == "__main__":
    start_processing()
