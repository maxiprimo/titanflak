import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# get bid/ask prices and bid-ask/middle price
def get_data(ma):
	f = open('coin123.txt')
	time_arr = []
	bid_arr = []
	ask_arr = []
	mid_arr = []
	while True:
	    line = f.readline()
	    if not line:
	        break
	    items = line.split("|");
	    time = int(items[0])
	    bid = float(items[1])
	    ask = float(items[2])
	    time_arr.append(time)
	    bid_arr.append(bid)
	    ask_arr.append(ask)
	    mid_arr.append(((ask-bid)/2)+bid)
	f.close()
	return time_arr[:], bid_arr[:], ask_arr[:], mid_arr[:]

ma = 10 # moving average
slide = 1000 # sliding window used to draw
time_arr, bid_arr, ask_arr, mid_arr = get_data(ma) # price data
size = len(time_arr)
day = 1440*60
offset = 1 # data offset
start = time_arr[offset] # start time

# virtual pocket
had = 100 # start cash
leverage = 50 # market leverage
out = 0
last = 0
trade = 0
vec = 0

# slide data through window
for j in range(int(size/slide)):
	
	# end after one day
	time = time_arr[offset]
	if(time > start + day):
		break

	# draw reset
	plt.clf()

	# iterate ask/bid-middle prices flow
	for i in range(slide):
		
		time = time_arr[offset+i]
		avg_p = mid_arr[offset+i] # current
		avg_p_last = mid_arr[offset+i-1] # last
		bid = bid_arr[offset+i]
		ask = ask_arr[offset+i]

		# direction
		buy = avg_p > avg_p_last and avg_p - avg_p_last > 0.1
		sell = avg_p < avg_p_last and avg_p_last - avg_p > 0.1

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
				print("buy_close:"+str(had)+"|price:"+str(bid)+"|time:"+str(time)+")");
			elif(buy):
				had = (out * last) + (out * (last - ask) * leverage)
				print("sell_close:"+str(had)+"|price:"+str(ask)+"|time:"+str(time)+")");
			out = 0
			last = 0

		# open buy or sell position
		if((buy or sell) and had != 0):
			trade = trade + 1
			if(sell):
				out = (had / bid)
				print("open_sell:"+str(had)+"|price:"+str(bid)+"|time:"+str(time)+")");
				last = bid
			elif(buy):
				out = (had / ask)
				print("open_buy:"+str(had)+"|price:"+str(ask)+"|time:"+str(time)+")");
				last = ask
			had = 0
		#else:
		#	print("none.")

	# draw window values
	#plt.plot(bid[offset:offset+slide], color='blue', linewidth=0.5);
	#plt.plot(ask[offset:offset+slide], color='red', linewidth=0.5);
	#plt.plot(mid_arr[offset:offset+slide], color='black', linewidth=0.5)
	#plt.show()

	# slide data
	offset = offset + slide
