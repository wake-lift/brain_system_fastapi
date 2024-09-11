import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler('errors.log', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)8s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
