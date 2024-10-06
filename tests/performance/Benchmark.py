import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OrderMatchingEngine import Order, Orderbook, Side, LimitOrder

from random import getrandbits, randint, random
import secrets

# Benchmark
OB = Orderbook()
numOrders = 10**2
orders = []
for n in range(numOrders):
	if bool(getrandbits(1)):
		orders.append(LimitOrder(n, Side.BUY, randint(1, 200), randint(1, 4)))
	else:
		orders.append(LimitOrder(n, Side.SELL, randint(1, 200), randint(1, 4)))

from time import time
start = time()
for order in orders:
	matches = OB.processOrder(order)
	if matches:
		for match in matches:
			print(f"Trade: Incoming Order ID: {order.id}, Price: {match.price}, Size: {match.size}, Incoming Side: {order.side}")
end = time()
totalTime = (end-start)
print("Time: " + str(totalTime))
print("Time per order (us): " + str(1000000*totalTime/numOrders))
print("Orders per second: " + str(numOrders/totalTime))

"""
Output
Time: 25.271270990371704
Time per order (us): 2.5271270990371706
Orders per second: 395706.25489354995
"""

print("All orders processed. Printing trades:")
for trade in OB.trades:
    print(trade)  # This will use the __str__ method we defined in the Trade class

print("\nPerformance metrics:")
print("Time: " + str(totalTime))
print("Time per order (us): " + str(1000000*totalTime/numOrders))
print("Orders per second: " + str(numOrders/totalTime))
