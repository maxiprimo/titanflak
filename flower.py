
# TitanFlak
# Easy Ultimate Capital. Slide The Exchange Wave. Big-Leverage, No-Commission, Low-Spread.
# MaxiPrimo 2021

import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# get bid/ask prices and bid-ask/middle price
def get_data():
	f = open('ticks.txt')
	time_arr = []
	bid_arr = []
	ask_arr = []
	mid_arr = []
	while True:
		line = f.readline()
		if not line:
			break
		items = line.split("|");
		time_arr.append(int(items[0]))
		bid = float(items[1])
		ask = float(items[2])
		bid_arr.append(bid)
		ask_arr.append(ask)
		mid_arr.append(((ask-bid)/2)+bid)
	f.close()
	return time_arr, bid_arr, ask_arr, mid_arr

slide = 11*60*30 # sliding window used to draw
step = 11*15
time_arr, bid_arr, ask_arr, mid_arr = get_data() # price data
size = len(time_arr)
day = 1440*60
offset = slide # data offset
start = time_arr[offset] # start time

# virtual pocket
had = 100 # start cash
leverage = 100 # market leverage
out = 0
last = 0
trade = 0
vec = 0

def get_kernel(stride, slide, step, array, offset):
	# kernel regression
	arr = []
	size = len(array)
	for i in range(0,slide,step):
		sum = 0
		sumw = 0
		for j in range(0,slide,step):
			w = math.exp(-(math.pow(i-j,2)/(stride*stride*2.0))) 
			sum = sum + array[offset-j-1] * w
			sumw = sumw + w
		arr.insert(0, sum/sumw)
	return arr;

# slide data through window
volume = []
last_zigzag = 0
for j in range(int(size/slide)):
	
	# end after one day
	time = time_arr[offset]
	if(time > start + day):
		break

	# draw reset
	plt.clf()

	# iterate ask/bid-middle prices flow
	for s in range(0, slide, step):
		
		time = time_arr[offset+s]
		bid = bid_arr[offset+s]
		ask = ask_arr[offset+s]
		mid = mid_arr[offset+s]

		# trend regression
		trend = get_kernel(int(slide/2), int(slide/1), step, mid_arr, offset+s)
		size = len(trend)
		trend_dist = (trend[size-1] - trend[size-2])*15
		x = [s, s]
		y = [trend[size-1], trend[size-1]+trend_dist]
		"""
		if(trend_dist > 0):
			plt.plot(x, y, color="blue", linewidth=0.5)
		if(trend_dist < 0):
			plt.plot(x, y, color="red", linewidth=0.5)
		"""
		# wave regression
		wave = get_kernel(int(slide/8), int(slide/4), step, mid_arr, offset+s)
		size = len(wave)
		wave_dist = (wave[size-1] - wave[size-2])*15*15
		x = [s, s]
		y = [wave[size-1], wave[size-1]+wave_dist]
		"""
		if(wave_dist > 0):
			plt.plot(x, y, color="yellow", linewidth=0.5)
		if(wave_dist < 0):
			plt.plot(x, y, color="gray", linewidth=0.5)
		"""
		# factor calculation
		factor = sum([trend_dist, wave_dist])
		"""
		x = [s, s]
		y = [bid_arr[offset]-250, bid_arr[offset]-250+(factor)];
		if(factor > 0):
			plt.plot(x, y, color="green", linewidth=0.5)
		elif(factor < 0):
			plt.plot(x, y, color="orange", linewidth=0.5)
		"""		
		volume.append(factor)
		size = int(slide/step)+1
		if(len(volume)<size):
			continue
		if(len(volume)>size):
			volume.pop(0)

		# zig zag regression
		zigzag = get_kernel(int(len(volume)/4), len(volume), 1, volume, len(volume))
		size = len(zigzag)
		zigzag_dist = (zigzag[size-1] - zigzag[size-2])*50
		x = [s, s]
		y = [bid_arr[offset]-250, bid_arr[offset]-250+zigzag_dist]
		if(zigzag_dist > 0):
			plt.plot(x, y, color="blue", linewidth=0.5)
		if(zigzag_dist < 0):
			plt.plot(x, y, color="red", linewidth=0.5)

		last_zigzag = zigzag_dist

		# decision
		buy = zigzag_dist > 0
		sell = zigzag_dist < 0

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
				print("step:"+str(s)+"|buy_close:"+str(had)+"|price:"+str(bid)+"|time:"+str(time)+")");
			elif(buy):
				had = (out * last) + (out * (last - ask) * leverage)
				print("step:"+str(s)+"|sell_close:"+str(had)+"|price:"+str(ask)+"|time:"+str(time)+")");
			out = 0
			last = 0

		# open buy or sell position
		if((buy or sell) and had != 0):
			trade = trade + 1
			if(buy):
				out = (had / ask)
				print("step:"+str(s)+"|open_buy:"+str(had)+"|price:"+str(ask)+"|time:"+str(time)+")");
				last = ask
			elif(sell):
				out = (had / bid)
				print("step:"+str(s)+"|open_sell:"+str(had)+"|price:"+str(bid)+"|time:"+str(time)+")");
				last = bid

			had = 0

	# draw window values
	plt.plot(bid_arr[offset:offset+slide], color='blue', linewidth=0.5)
	plt.plot(ask_arr[offset:offset+slide], color='red', linewidth=0.5);
	plt.plot(mid_arr[offset:offset+slide], color='black', linewidth=0.5)
	plt.show()

	# slide data
	offset = offset + slide
