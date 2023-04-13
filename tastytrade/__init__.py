import logging
import sys

log = logging.getLogger(__name__)
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
