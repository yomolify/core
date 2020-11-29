CSMR

side
sell
params
{'exectype': None}
amount
3910.394363737283
price
None
order_type
market
side
buy
params
{'exectype': None}
Broker next() called
Fetching Order ID: 314303169
Traceback (most recent call last):
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 588, in fetch
    response.raise_for_status()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/requests/models.py", line 941, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/order?timestamp=1605679369870&recvWindow=5000&symbol=ALGOUSDT&orderId=314303169&signature=eb7cc41705bd2548999ca5afff0cf6375df32df1be61cff18e4bb585d4a5e32a

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "main.py", line 168, in <module>
    cerebro, strat = _run_resampler(data_timeframe=bt.TimeFrame.Minutes,
  File "main.py", line 157, in _run_resampler
    res = cerebro.run()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1127, in run
    runstrat = self.runstrategies(iterstrat)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1298, in runstrategies
    self._runnext(runstrats)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1623, in _runnext
    self._brokernotify()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1360, in _brokernotify
    self._broker.next()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtbroker.py", line 201, in next
    ccxt_order = self.store.fetch_order(oID, o_order.data.p.dataname)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtstore.py", line 143, in retry_method
    return method(self, *args, **kwargs)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtstore.py", line 192, in fetch_order
    return self.exchange.fetch_order(oid, symbol)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 1679, in fetch_order
    response = getattr(self, method)(self.extend(request, query))
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 465, in inner
    return entry(_self, **inner_kwargs)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 2405, in request
    response = self.fetch2(path, api, method, params, headers, body)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 486, in fetch2
    return self.fetch(request['url'], request['method'], request['headers'], request['body'])
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 604, in fetch
    self.handle_errors(http_status_code, http_status_text, url, method, headers, http_response, json_response, request_headers, request_body)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 2399, in handle_errors
    self.throw_exactly_matched_exception(self.exceptions, error, feedback)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 504, in throw_exactly_matched_exception
    raise exact[string](message)
ccxt.base.errors.OrderNotFound: binance {"code":-2013,"msg":"Order does not exist."}







=======================





Broker next() called
Fetching Order ID: 77697653
Traceback (most recent call last):
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 588, in fetch
    response.raise_for_status()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/requests/models.py", line 941, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://fapi.binance.com/fapi/v1/order?timestamp=1606212665794&recvWindow=5000&symbol=KSMUSDT&orderId=77697653&signature=d1ea25312848477132471aa4bdbb7ee5409b08269bbe9347e899c8db891e8efc

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "main.py", line 168, in <module>
    cerebro, strat = _run_resampler(data_timeframe=bt.TimeFrame.Minutes,
  File "main.py", line 157, in _run_resampler
    res = cerebro.run()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1127, in run
    runstrat = self.runstrategies(iterstrat)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1298, in runstrategies
    self._runnext(runstrats)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1623, in _runnext
    self._brokernotify()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/backtrader/cerebro.py", line 1360, in _brokernotify
    self._broker.next()
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtbroker.py", line 201, in next
    ccxt_order = self.store.fetch_order(oID, o_order.data.p.dataname)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtstore.py", line 143, in retry_method
    return method(self, *args, **kwargs)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxtbt/ccxtstore.py", line 192, in fetch_order
    return self.exchange.fetch_order(oid, symbol)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 1679, in fetch_order
    response = getattr(self, method)(self.extend(request, query))
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 465, in inner
    return entry(_self, **inner_kwargs)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 2405, in request
    response = self.fetch2(path, api, method, params, headers, body)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 486, in fetch2
    return self.fetch(request['url'], request['method'], request['headers'], request['body'])
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 604, in fetch
    self.handle_errors(http_status_code, http_status_text, url, method, headers, http_response, json_response, request_headers, request_body)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/binance.py", line 2399, in handle_errors
    self.throw_exactly_matched_exception(self.exceptions, error, feedback)
  File "/home/ec2-user/.local/lib/python3.8/site-packages/ccxt/base/exchange.py", line 504, in throw_exactly_matched_exception
    raise exact[string](message)
ccxt.base.errors.OrderNotFound: binance {"code":-2013,"msg":"Order does not exist."}