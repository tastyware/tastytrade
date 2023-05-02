import logging
import sys

API_URL = 'https://api.cert.tastyworks.com'
VERSION = '1.0'

log = logging.getLogger(__name__)
logging.getLogger('aiocometd').setLevel(logging.CRITICAL)
log.propagate = False
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

root = logging.getLogger()
root.addHandler(out_hdlr)
root.propagate = False
root.setLevel(logging.INFO)
