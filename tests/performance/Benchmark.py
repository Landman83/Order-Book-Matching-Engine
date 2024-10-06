import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OrderMatchingEngine import Order, Orderbook, Side, LimitOrder
from OrderMatchingEngine.Packager import create_settleable_matched_orders, SettleableMatchedOrder

from random import getrandbits, randint, random
import secrets

# Benchmark
OB = Orderbook()
numOrders = 10**1
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

# After your benchmark is complete and trades are processed, add:

print("\nCreating Settleable Matched Orders:")
cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token

settleable_orders = create_settleable_matched_orders(OB, cash_token, security_token)

print(f"Total Settleable Matched Orders: {len(settleable_orders)}")

# Print the first 5 settleable orders (or all if less than 5)
for i, order in enumerate(settleable_orders[:5], 1):
    print(f"\nSettleable Order {i}:")
    print(f"  Cash Amount: {order.cashAmount}")
    print(f"  Security Amount: {order.securityAmount}")
    print(f"  Buyer: {order.buyer}")
    print(f"  Seller: {order.seller}")
    print(f"  Cash Token: {order.cashToken}")
    print(f"  Security Token: {order.securityToken}")
    print(f"  Maker: {order.maker}")
    print(f"  Taker: {order.taker}")

if len(settleable_orders) > 5:
    print("\n... (remaining orders omitted for brevity)")