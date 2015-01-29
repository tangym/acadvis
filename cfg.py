import logging
import logging.handlers

LOG_FILE = 'db_manage.log'
log = logging.getLogger('user')

handler = logging.handlers.RotatingFileHandler(LOG_FILE)
fmt = '%(asctime)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
log.addHandler(handler)

handler = logging.StreamHandler()
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
log.addHandler(handler)

log.setLevel(logging.DEBUG)


DB_HOST = 'localhost'
DB_PORT = 6379

BIB_LIST_FILE = 'bib.txt'
with open(BIB_LIST_FILE) as f:
    BIB_LIST = map(lambda e: e.strip(), f)
    BIB_LIST = filter(lambda e: e, BIB_LIST)
    BIB_LIST = list(BIB_LIST)

LEXICON_FILE = 'lexicon.json'
