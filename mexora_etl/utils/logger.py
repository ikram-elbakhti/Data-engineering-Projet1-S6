import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Configure et retourne un logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler pour l'ETL
        # fh = logging.FileHandler('etl.log')
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
        
    return logger
