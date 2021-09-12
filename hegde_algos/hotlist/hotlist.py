import yfinance as yf
import pandas as pd

apple = yf.Ticker('AAPL')


print(apple.get_cashflow())