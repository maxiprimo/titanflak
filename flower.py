import sys
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# get bid/ask prices and bid-ask/middle price
def get_data(ma):
	f = open('market.txt')
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
	avg_arr = pd.DataFrame(data=mid_arr, columns=["Avg"]).rolling(ma).mean().values;
	return time_arr[ma:], bid_arr[ma:], ask_arr[ma:], mid_arr[ma:], avg_arr[ma:]

ma = 100 # moving average
slide = 1000 # sliding window used to draw
time_arr, bid_arr, ask_arr, mid_arr, avg_arr = get_data(ma) # price data
size = len(time_arr)
day = 1440*60
offset = 1 # data offset
start = time_arr[offset] # start time
ma_list = []
ma_curr = 0
ma_last = 0
ma_arr = []

# virtual pocket
had = 100 # start cash
leverage = 100 # market leverage
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
		
		# moving average
		ma_list.append(mid_arr[offset+i])
		if(len(ma_list)<=ma):
			ma_arr.append(mid_arr[i])
			continue
		ma_list = ma_list[1:]
		sum = 0
		for s in range(ma):
			sum = sum + ma_list[s]
		ma_curr = sum/ma
		if(ma_last == 0):
			ma_last = ma_curr
			continue
		ma_arr.append(ma_curr)

		time = time_arr[offset+i]

		bid = bid_arr[offset+i]
		ask = ask_arr[offset+i]

		# direction
		buy = ma_curr > ma_last and ma_curr - ma_last > 0.1
		sell = ma_curr < ma_last and ma_last - ma_curr > 0.1

		ma_last = ma_curr

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
	#plt.plot(bid_arr[offset:offset+slide], color='blue', linewidth=0.5);
	#plt.plot(ask_arr[offset:offset+slide], color='red', linewidth=0.5);
	#plt.plot(mid_arr[offset:offset+slide], color='black', linewidth=0.5)
	#plt.plot(avg_arr[offset:offset+slide], color='green', linewidth=0.5)
	#plt.plot(ma_arr[offset:offset+slide], color='orange', linewidth=0.5)
	#plt.show()

	# slide data
	offset = offset + slide
