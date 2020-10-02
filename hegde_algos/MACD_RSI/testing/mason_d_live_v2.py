import pandas as pd
import backtrader as bt 
import yfinance as y 


#***********************************************************************
#	V2 of live trading attempts to impliment using trading more
# 	than one stock on the TWS system API as well as live data 
#	notifications and connection mangement incase of disconnect
#***********************************************************************

class macd_rsi_ma_swtich(bt.Strategy):

	def __init__(self):

		self.inds = dict()
		for i, d in enumerate(self.datas):
			self.inds[d] = dict()
			self.inds[d]['movav'] = bt.indicators.SimpleMovingAverage(d.close, period = 9)
			self.inds[d]['rsi'] = bt.indicators.RSI_SMA(d.close,plot = False)
			self.inds[d]['mac'] = bt.indicators.MACD(d.close, plot = False)
			self.inds[d]['macd'] = self.inds[d]['mac'].lines.macd
			self.inds[d]['mac_signal'] = self.inds[d]['mac'].lines.signal
			self.inds[d]['macd_cross'] = bt.indicators.CrossOver(self.inds[d]['macd'], self.inds[d]['mac_signal'], plot=False)
			self.inds[d]['rsi_entry'] = False
			self.inds[d]['macd_entry'] = False
			self.inds[d]['enter_price'] = 0

	def notify_data(self, data, status, *args, **kwargs):
		if status == data.DISCONNECTED:
			print("Disconnected: ", data.DISCONNECTED)
			exit(1)
		if status == data.CONNBROKEN:
			print("Connection Lost")
		if status == data.CONNECTED:
			print("Connected")
		if status == data.LIVE:
			print("Data Live")
		if status == data.NOTSUBSCRIBED:
			print("Error Retriving Data:", data.NOTSUBSCRIBED)
		if status == data.DELAYED:
			print("Data is not live")


	def notify_order(self, order):
		if order.status == order.Submitted:
			print("Order Submitted")
		if order.status == order.Completed:
			buysell = 'Buy' if order.isbuy() else 'Sell'
			txt = '{} {}@{}'.format(buysell, order.executed.size, order.executed.price)
			print(txt)
		if order.status == order.Cancelled:
			print("Error Order Cancelled")

	def notify_trade(self, trade):
		if not trade.isclosed:
			return
		print('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

	def next(self):
		for i, d in enumerate(self.datas):
			dn = d._name
			pos = self.getposition(d).size
			if not pos:
				if self.inds[d]['rsi'][0] <= 30:
					self.inds[d]['rsi_entry'] = True
				if self.inds[d]['rsi_entry'] == True:
					if self.inds[d]['macd_cross'][0] == 1.0:
						self.inds[d]['macd_entry'] = True
				if self.inds[d]['rsi_entry'] == True and self.inds[d]['macd_entry'] == True and d.close[0] >= self.inds[d]['movav']:
					self.order = self.buy(data = d, size = 10)
					self.inds[d]['enter_price'] = d.close[0]
					self.inds[d]['rsi_entry'] = False
					self.inds[d]['macd_entry'] = False
			else:
				if self.inds[d]['macd_cross'] == -1.0:
					self.close(data = d, size = 10) 


cerebro = bt.Cerebro()
ibstore = bt.stores.IBStore(host = '127.0.0.1', port = 7497, clientId = 35)
cerebro.broker = ibstore.getbroker()

stock_names = ['TWTR', 'AAPL', 'AMD', 'NKE','C','NVDA','CDLX','KEGX']

for i in range(len(stock_names)):
	dname = stock_names[i] + '-STK-SMART'
	ibd = ibstore.getdata(dataname = dname, rtbar = True)
	cerebro.resampledata(ibd, timeframe = bt.TimeFrame.Minutes, compression = 30)
	cerebro.adddata(ibd)

cerebro.addstrategy(macd_rsi_ma_swtich)
cerebro.run()
cerebro.plot(style = 'line')