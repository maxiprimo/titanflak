
# TitanFlak
# Easy Ultimate Capital. Slide The Crypto Exchange Wave. Big-Leverage, No-Commission, Low-Spread.
# MaxiPrimo 2021

import sys
import os
import math
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

def get_relative(data):
	result = []
	for i in range(1, len(data)):
		result.append(data[i]-data[i-1])
	return result

def get_absolute(data):
	result = [100*1000]
	for i in range(len(data)):
		result.append(result[-1]+data[i])
	return result

# get close price ticks
def get_data(path, step):
	f = open(path)
	bid_arr = []
	ask_arr = []
	close_arr = []
	count = 0
	while True:
		line = f.readline()
		if not line:
			break
		items = line.split("|");
		if(count%step==0):
			bid_arr.append(float(items[1]))
			ask_arr.append(float(items[2]))
			close_arr.append(float(items[3]))
		count = count+1
	f.close()
	return bid_arr, ask_arr, close_arr

def series_to_supervised(data, n_in, n_out):
	n_vars = 1 if type(data) is list else data.shape[1]
	df = pd.DataFrame(data)
	cols = list()
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
	for i in range(0, n_out):
		cols.append(df.shift(-i))
	agg = pd.concat(cols, axis=1)
	agg.dropna(inplace=True)
	return agg.values
 
def run_forecast(model, past, steps):
	forecast = []
	for i in range(steps):
		test = series_to_supervised(past, n_in=steps_in, n_out=steps_out)
		yhat = model.predict(np.asarray([test[0, :-1]]))
		past.append(yhat[-1])
		forecast.append(yhat[-1])
		past = past[1:]
	return forecast

def run_train(train, new_or_exit=True):
	if(new_or_exit):
		history = [x for x in train]
		train = np.asarray(train)
		trainX, trainy = train[:, :-1], train[:, -1]
		model = XGBRegressor(n_estimators=1500, random_state=7, tree_method='hist')
		model.fit(trainX, trainy)
		pickle.dump(model, open("model.pkl", "wb"))
		return model
	else:
		model = pickle.load(open("model.pkl", "rb"))
		return model

seconds = 3
bid_arr, ask_arr, close_arr = get_data('market.txt', int(seconds*6)) # price data
close_arr = get_relative(close_arr)
offset = -10*1000
begin = offset-1000*1000
data = close_arr[begin:offset] # train data
steps_in, steps_out = int(180/seconds),int(60/seconds) # windows
span = steps_in+steps_out
new = False # train new or load model
train = []
if(new):
	train = series_to_supervised(data, n_in=steps_in, n_out=steps_out)
model = run_train(train, new)
test = close_arr[offset:] # forecast data
bid_arr = bid_arr[offset:]
ask_arr = ask_arr[offset:]

# virtual pocket
had = 100 # start cash
leverage = 100 # market leverage
out = 0
last = 0
trade = 0
vec = 0

# forecast
for i in range(0, len(test), steps_out):

	# do forecast
	past = test[i:i+span+int(60/seconds)]
	future = test[i+span+int(60/seconds):i+span+int(60/seconds)+(steps_out)]
	forecast = run_forecast(model, past, steps_out)
	error = mean_absolute_error(future, forecast)
	print("mean_error:"+str(error))

	for j in range(len(forecast)-1):

		# decision
		diff = forecast[j+1] - forecast[j]
		buy = diff > 0
		sell = diff < 0

		bid = bid_arr[i+span+int(60/seconds)+j]
		ask = ask_arr[i+span+int(60/seconds)+j]
		
		# hold or switch direction
		finish = True
		if(buy and vec <= 0):
			vec = 1
		elif(sell and vec >= 0):
			vec = -1
		else:
			finish = False

		# close open position
		if(finish and out != 0):
			trade = trade + 1
			if(sell):
				had = (out * last) + (out * (bid - last) * leverage)
				print("step:"+str(i)+"|buy_close:"+str(had)+"|price:"+str(bid));
			elif(buy):
				had = (out * last) + (out * (last - ask) * leverage)
				print("step:"+str(i)+"|sell_close:"+str(had)+"|price:"+str(ask));
			out = 0
			last = 0
		# open buy or sell position
		if((buy or sell) and had != 0):
			trade = trade + 1
			if(buy):
				out = (had / ask)
				print("step:"+str(i)+"|open_buy:"+str(had)+"|price:"+str(ask));
				last = ask
			elif(sell):
				out = (had / bid)
				print("step:"+str(i)+"|open_sell:"+str(had)+"|price:"+str(bid));
				last = bid
			had = 0

	plt.plot(get_absolute(future), color='black', linewidth=0.5)
	plt.plot(get_absolute(forecast), color='red', linewidth=0.5)
	plt.show()
