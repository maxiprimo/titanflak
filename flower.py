import sys
import math
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

slide = 11*60*5 # sliding window used to draw
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

# slide data through window
for j in range(int(size/slide)):
	
	# end after one day
	time = time_arr[offset]
	if(time > start + day):
		break

	# draw reset
	plt.clf()

	# get value difference
	bid_low = 1000*1000
	ask_high = 0
	bidask = 0
	highlow = 0
	for i in range(slide):
		idx = offset+i-slide
		bidask = bidask + (ask_arr[idx] - bid_arr[idx])
		if(bid_arr[idx] < bid_low):
			bid_low = bid_arr[idx]
		if(ask_arr[idx] > ask_high):
			ask_high = ask_arr[idx]
	bidask = bidask/slide
	highlow = ask_high - bid_low
	valuescale = bidask / highlow

	# iterate ask/bid-middle prices flow
	step = 15
	for s in range(0, slide, step):
		
		time = time_arr[offset+s]
		bid = bid_arr[offset+s]
		ask = ask_arr[offset+s]
		mid = mid_arr[offset+s]

		# kernel regression
		arr = []
		stride = 50 * pow(1+(1-valuescale), 3)
		for i in range(0, slide,step):
			sum = 0
			sumw = 0
			for j in range(0, slide,step):
				w = math.exp(-(math.pow(i-j,2)/(stride*stride*2.0)))
				idx = offset+s-j-1
				value = mid_arr[idx]
				sum = sum + value * w
				sumw = sumw + w
			arr.insert(0, sum/sumw)

		# direction
		buy = arr[len(arr)-1] > arr[len(arr)-2]
		sell = arr[len(arr)-1] < arr[len(arr)-2]

		x = [s-5, s]
		y = [arr[len(arr)-2], arr[len(arr)-1]]

		if(buy):
			plt.plot(x, y, color="blue", linewidth=0.5)
		if(sell):
			plt.plot(x, y, color="red", linewidth=0.5)

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
	#plt.plot(bid_arr[offset:offset+slide], color='blue', linewidth=0.5)
	#plt.plot(ask_arr[offset:offset+slide], color='red', linewidth=0.5);
	#plt.plot(mid_arr[offset:offset+slide], color='black', linewidth=0.5)
	#plt.show()

	# slide data
	offset = offset + slide
