import pandas as pd
import backtrader as bt 
import yfinance as y 


#data_30m = y.download(tickers = 'TWTR', period = '60d', interval = '30m')
#data_30m.to_csv('TWTR_30m.csv')


data_p = pd.read_csv('TWTR_30m.csv', index_col = 0, parse_dates = True)
data_p.drop(columns = ['Adj Close'])


def get_share_size(account_val, risk, buy_price, stop_price):
	amount = account_val*risk
	total = amount/(buy_price - stop_price)
	return total/2

class macd_rsi_ma_swtich(bt.Strategy):

	def __init__(self):
		self.close_price = self.datas[0].close
		self.movav = bt.indicators.SimpleMovingAverage(self.data, period = 9)
		self.mac = bt.indicators.MACD(self.data).lines.macd
		self.mac_signal = bt.indicators.MACD(self.data).lines.signal
		self.macd_cross = bt.indicators.CrossOver(self.mac, self.mac_signal)
		self.rsi = bt.indicators.RSI_SMA(self.data)
		self.rsi_entry = False
		self.macd_entry = False
		self.stop_price = 0
		self.enter_size = 0
		self.enter_price = 0
		self.order = None

	def notify_order(self, order):
		if order.status == order.Completed:
			buysell = 'Buy' if order.isbuy() else 'Sell'
			txt = '{} {}@{}'.format(buysell, order.executed.size, order.executed.price)
			print(txt)

	def next(self):
		if not self.position:
			if self.rsi_entry == True:
				if self.macd_cross == 1.0:
					self.macd_entry = True
			if self.rsi <= 30:
				self.rsi_entry = True
			if self.rsi_entry == True and self.macd_entry == True and self.close_price[0] >= self.movav:
				self.stop_price = self.close_price[0] * (1-0.02)
				self.target = self.close_price[0] * (1+0.10)
				self.enter_size = get_share_size(self.broker.getvalue(), 0.02, self.close_price[0], self.stop_price)
				self.order = self.buy(size = self.enter_size, exectype = bt.Order.StopTrail, trailpercent= 0.02)
				self.enter_price = self.close_price[0]
				self.rsi_entry = False
				self.macd_entry = False
		else:
			#if self.stop_price >= self.close_price[0]:
			#	self.close(size = self.enter_price)
		#		print('STOPPED OUT RSI,MACDENTRY:', self.rsi[0], self.macd_entry,self.enter_size)
			if self.macd_cross == -1.0:
				self.close(size = self.enter_size) 


cerebro = bt.Cerebro()
cerebro.broker.setcash(10000.00)
cerebro.broker.setcommission(commission = 0.0)
data = bt.feeds.PandasData(dataname = data_p)
cerebro.adddata(data)
cerebro.addstrategy(macd_rsi_ma_swtich)
cerebro.run()
cerebro.plot(style = 'line')