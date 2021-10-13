import sys
import os
import datetime
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# get bid/ask prices, bid-ask/middle price and bid-ask/middle moving average
def get_data(ma):
	f = open('coin123.txt')
	data = []
	data1 = []
	while True:
	    line = f.readline()
	    if not line:
	        break
	    items = line.split("|");
	    time = int(items[0])
	    bid = float(items[1])
	    ask = float(items[2])
	    data.append([bid, ask, time])
	    data1.append(((ask-bid)/2)+bid)
	f.close()
	result = pd.DataFrame(data=data1, columns=["Avg"]);
	rolling_mean = result.rolling(window=ma).mean()
	return data[ma:], result.values[ma:], rolling_mean.values[ma:]

slide = 1000 # sliding window used to draw
ma = 10 # moving average
prices, plain, avg = get_data(ma) # prices data
size = len(plain)
day = 1440*60
offset = 0
start = prices[0][2] # start time

# virtual pocket
had = 100 # start cash
out = 0
last = 0
trade = 0
vec = 0

# slide data through window
for i in range(int(size/slide)):
	
	# end after one day
	time = prices[offset][2]
	if(time > start + day):
		break

	# iterate ask/bid middle average prices flow
	for i in range(1, slide):

		avg_p = avg[offset+i] # current
		avg_p_last = avg[offset+i-1] # last

		bid = prices[offset+i][0]
		ask = prices[offset+i][1]

		# direction
		buy = avg_p > avg_p_last 
		sell = avg_p < avg_p_last

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
				had = (out * last) + (out * (bid - last) * 50)
				print("buy_close:"+str(had)+"|price:"+str(bid)+")");
			elif(buy):
				had = (out * last) + (out * (last - ask) * 50)
				print("sell_close:"+str(had)+"|price:"+str(ask)+")");
			out = 0
			last = 0

		# open buy or sell position
		if((buy or sell) and had != 0):
			trade = trade + 1
			if(sell):
				out = (had / bid)
				print("open_sell:"+str(had)+"|price:"+str(bid)+")");
				last = bid
			elif(buy):
				out = (had / ask)
				print("open_buy:"+str(had)+"|price:"+str(ask)+")");
				last = ask
			had = 0

	# draw window values
	#plt.clf()
	#plt.plot(plain[offset:offset+slide], color='blue', linewidth=0.5);
	#plt.plot(avg[offset:offset+slide], color='red', linewidth=0.5);
	#plt.plot(idx, xy, color='black', linewidth=0.5);
	#plt.show()

	# slide data
	offset = offset + slide
