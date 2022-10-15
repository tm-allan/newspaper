import sys
import logging
from logging.handlers import RotatingFileHandler


LOG_FILE = 'logs.log'
# if config.DEBUG:
#     LOG_LEVEL = logging.DEBUG
# else:
#     LOG_LEVEL = logging.INFO
LOG_LEVEL = logging.INFO
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)
fh = RotatingFileHandler(LOG_FILE, maxBytes=10000000, backupCount=3)
fh.setLevel(LOG_LEVEL)
# create formatter and add it to the handlers
formatter = logging.Formatter(fmt='%(levelname).1s %(asctime)s.%(msecs).03d: %(message)s [%(pathname)s:%(lineno)d]', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
LOGGER = logging.getLogger('newspaper')
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(ch)
LOGGER.addHandler(fh)
LOGGER.propagate = False
