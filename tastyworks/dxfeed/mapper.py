import logging

from tastyworks.dxfeed import greeks, profile, quote, summary, trade

LOGGER = logging.getLogger(__name__)
KEY_MAP = {}


def map_message(message):
    if isinstance(message[0], str):
        first_sample = False
    else:
        first_sample = True
    msg_type = message[0][0] if first_sample else message[0]

    if quote.Quote.DXFEED_TEXT == msg_type:
        res = quote.Quote(data=message)
    elif greeks.Greeks.DXFEED_TEXT == msg_type:
        res = greeks.Greeks(data=message)
    elif trade.Trade.DXFEED_TEXT == msg_type:
        res = trade.Trade(data=message)
    elif summary.Summary.DXFEED_TEXT == msg_type:
        res = summary.Summary(data=message)
    elif profile.Profile.DXFEED_TEXT == msg_type:
        res = profile.Profile(data=message)
    else:
        LOGGER.warning("Unknown message type received from streamer: {}".format(message))
        res = [{'warning': 'Unknown message type received', 'message': message}]

    return res
