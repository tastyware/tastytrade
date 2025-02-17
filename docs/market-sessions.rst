Market Sessions
===============

A market time session object contains information about the current state of specific markets. It can be used to get the market opening and closing times and state.

The dataclass represents the current session and any nested 'next' or 'previous' session info.

The ``get_market_sessions`` function can be used to obtain information about the current session:

.. code-block:: python

   from tastytrade.market_sessions import ExchangeType, get_market_sessions
   get_market_sessions(session, exchanges=[ExchangeType.NYSE])

>>> [MarketSession(close_at=None, close_at_ext=None, instrument_collection='Equity', open_at=None, start_at=None, next_session=MarketSessionSnapshot(close_at=datetime.datetime(2025, 2, 18, 21, 0, tzinfo=TzInfo(UTC)), close_at_ext=datetime.datetime(2025, 2, 19, 1, 0, tzinfo=TzInfo(UTC)), instrument_collection='Equity', open_at=datetime.datetime(2025, 2, 18, 14, 30, tzinfo=TzInfo(UTC)), session_date=datetime.date(2025, 2, 18), start_at=datetime.datetime(2025, 2, 18, 13, 15, tzinfo=TzInfo(UTC))), previous_session=MarketSessionSnapshot(close_at=datetime.datetime(2025, 2, 14, 21, 0, tzinfo=TzInfo(UTC)), close_at_ext=datetime.datetime(2025, 2, 15, 1, 0, tzinfo=TzInfo(UTC)), instrument_collection='Equity', open_at=datetime.datetime(2025, 2, 14, 14, 30, tzinfo=TzInfo(UTC)), session_date=datetime.date(2025, 2, 14), start_at=datetime.datetime(2025, 2, 14, 13, 15, tzinfo=TzInfo(UTC))), status=<MarketStatus.CLOSED: 'Closed'>)]

The ``get_market_holidays`` function can be used to obtain information about markets half days and holidays:

.. code-block:: python

   from tastytrade.market_sessions import get_market_holidays
   calendar = Market.get_market_holidays(session)
   print(calendar.half_days)
   print(calendar.holidays)

>>> [datetime.date(2015, 12, 24), datetime.date(2016, 11, 25), datetime.date(2017, 7, 3), datetime.date(2017, 11, 24), datetime.date(2018, 7, 3), datetime.date(2018, 11, 23), datetime.date(2018, 12, 24), datetime.date(2019, 7, 3), datetime.date(2019, 11, 29), datetime.date(2019, 12, 24), datetime.date(2020, 11, 27), datetime.date(2020, 12, 24), datetime.date(2021, 11, 26), datetime.date(2022, 11, 25), datetime.date(2023, 7, 3), datetime.date(2023, 11, 24), datetime.date(2024, 7, 3), datetime.date(2024, 11, 29), datetime.date(2024, 12, 24), datetime.date(2025, 7, 3), datetime.date(2025, 11, 28), datetime.date(2025, 12, 24), datetime.date(2026, 11, 27), datetime.date(2026, 12, 24), datetime.date(2027, 7, 2), datetime.date(2027, 11, 26), datetime.date(2027, 12, 23), datetime.date(2028, 7, 3), datetime.date(2028, 11, 24), datetime.date(2028, 12, 22), datetime.date(2029, 7, 3)]
>>> [datetime.date(2015, 12, 25), datetime.date(2016, 1, 1), datetime.date(2016, 1, 18), datetime.date(2016, 2, 15), datetime.date(2016, 3, 25), datetime.date(2016, 5, 30), datetime.date(2016, 7, 4), datetime.date(2016, 9, 5), datetime.date(2016, 11, 24), datetime.date(2016, 12, 26), datetime.date(2017, 1, 2), datetime.date(2017, 1, 16), datetime.date(2017, 2, 20), datetime.date(2017, 4, 14), datetime.date(2017, 5, 29), datetime.date(2017, 7, 4), datetime.date(2017, 9, 4), datetime.date(2017, 11, 23), datetime.date(2017, 12, 25), datetime.date(2018, 1, 1), datetime.date(2018, 1, 15), datetime.date(2018, 2, 19), datetime.date(2018, 3, 30), datetime.date(2018, 5, 28), datetime.date(2018, 7, 4), datetime.date(2018, 9, 3), datetime.date(2018, 11, 22), datetime.date(2018, 12, 5), datetime.date(2018, 12, 25), datetime.date(2019, 1, 1), datetime.date(2019, 1, 21), datetime.date(2019, 2, 18), datetime.date(2019, 4, 19), datetime.date(2019, 5, 27), datetime.date(2019, 7, 4), datetime.date(2019, 9, 2), datetime.date(2019, 11, 28), datetime.date(2019, 12, 25), datetime.date(2020, 1, 1), datetime.date(2020, 1, 20), datetime.date(2020, 2, 17), datetime.date(2020, 4, 10), datetime.date(2020, 5, 25), datetime.date(2020, 7, 3), datetime.date(2020, 9, 7), datetime.date(2020, 11, 26), datetime.date(2020, 12, 25), datetime.date(2021, 1, 1), datetime.date(2021, 1, 18), datetime.date(2021, 2, 15), datetime.date(2021, 4, 2), datetime.date(2021, 5, 31), datetime.date(2021, 7, 5), datetime.date(2021, 9, 6), datetime.date(2021, 11, 25), datetime.date(2021, 12, 24), datetime.date(2022, 1, 17), datetime.date(2022, 2, 21), datetime.date(2022, 4, 15), datetime.date(2022, 5, 30), datetime.date(2022, 6, 20), datetime.date(2022, 7, 4), datetime.date(2022, 9, 5), datetime.date(2022, 11, 24), datetime.date(2022, 12, 26), datetime.date(2023, 1, 2), datetime.date(2023, 1, 16), datetime.date(2023, 2, 20), datetime.date(2023, 4, 7), datetime.date(2023, 5, 29), datetime.date(2023, 6, 19), datetime.date(2023, 7, 4), datetime.date(2023, 9, 4), datetime.date(2023, 11, 23), datetime.date(2023, 12, 25), datetime.date(2024, 1, 1), datetime.date(2024, 1, 15), datetime.date(2024, 2, 19), datetime.date(2024, 3, 29), datetime.date(2024, 5, 27), datetime.date(2024, 6, 19), datetime.date(2024, 7, 4), datetime.date(2024, 9, 2), datetime.date(2024, 11, 28), datetime.date(2024, 12, 25), datetime.date(2025, 1, 1), datetime.date(2025, 1, 9), datetime.date(2025, 1, 20), datetime.date(2025, 2, 17), datetime.date(2025, 4, 18), datetime.date(2025, 5, 26), datetime.date(2025, 6, 19), datetime.date(2025, 7, 4), datetime.date(2025, 9, 1), datetime.date(2025, 11, 27), datetime.date(2025, 12, 25), datetime.date(2026, 1, 1), datetime.date(2026, 1, 19), datetime.date(2026, 2, 16), datetime.date(2026, 4, 3), datetime.date(2026, 5, 25), datetime.date(2026, 6, 19), datetime.date(2026, 7, 3), datetime.date(2026, 9, 7), datetime.date(2026, 11, 26), datetime.date(2026, 12, 25), datetime.date(2027, 1, 1), datetime.date(2027, 1, 18), datetime.date(2027, 2, 15), datetime.date(2027, 3, 26), datetime.date(2027, 5, 31), datetime.date(2027, 6, 18), datetime.date(2027, 7, 5), datetime.date(2027, 9, 6), datetime.date(2027, 11, 25), datetime.date(2027, 12, 24), datetime.date(2028, 1, 17), datetime.date(2028, 2, 21), datetime.date(2028, 4, 14), datetime.date(2028, 5, 29), datetime.date(2028, 6, 19), datetime.date(2028, 7, 4), datetime.date(2028, 9, 4), datetime.date(2028, 11, 23), datetime.date(2028, 12, 25), datetime.date(2029, 1, 1), datetime.date(2029, 1, 15), datetime.date(2029, 2, 19), datetime.date(2029, 3, 30), datetime.date(2029, 5, 28), datetime.date(2029, 6, 19), datetime.date(2029, 7, 4), datetime.date(2029, 9, 3)]

I case you only want to extract the market status, this is one way to do it:

.. code-block:: python

   from tastytrade.market_sessions import ExchangeType, MarketStatus, get_market_sessions

   market_sessions = get_market_sessions(session, exchanges=[ExchangeType.NYSE, ExchangeType.CME])
   print([ms.status != MarketStatus.CLOSED for ms in market_sessions])

>>> [False, False]
