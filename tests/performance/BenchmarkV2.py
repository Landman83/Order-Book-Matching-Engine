import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OrderMatchingEngine import Order, Orderbook, Side, LimitOrder
from OrderMatchingEngine.PackagerV2 import create_settlement_ready_trades

from random import getrandbits, randint
import time

# Benchmark
OB = Orderbook()
numOrders = 10**4
orders = []
for n in range(numOrders):
	if bool(getrandbits(1)):
		orders.append(LimitOrder(n, Side.BUY, randint(1, 200), randint(1, 4)))
	else:
		orders.append(LimitOrder(n, Side.SELL, randint(1, 200), randint(1, 4)))

start = time.time()
for order in orders:
	OB.processOrder(order)
end = time.time()
totalTime = (end-start)

print("\nPerformance metrics:")
print("Time: " + str(totalTime))
print("Time per order (us): " + str(1000000*totalTime/numOrders))
print("Orders per second: " + str(numOrders/totalTime))

# Create Settlement Ready Trades
print("\nCreating Settlement Ready Trades:")
cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token
fee_recipient = "0xfedc000000000000000000000000000000000000"  # Example Ethereum address for fee recipient

settlement_ready_trades = create_settlement_ready_trades(OB, cash_token, security_token, fee_recipient)

print(f"Total Settlement Ready Trades: {len(settlement_ready_trades)}")

# Print the first 5 settlement ready trades (or all if less than 5)
for i, trade in enumerate(settlement_ready_trades[:5], 1):
	print(f"\nSettlement Ready Trade {i}:")
	print(f"  Maker Token: {trade.makerToken}")
	print(f"  Taker Token: {trade.takerToken}")
	print(f"  Maker Amount: {trade.makerAmount}")
	print(f"  Taker Amount: {trade.takerAmount}")
	print(f"  Maker: {trade.maker}")
	print(f"  Taker: {trade.taker}")
	print(f"  Sender: {trade.sender}")
	print(f"  Fee Recipient: {trade.feeRecipient}")
	print(f"  Pool: {trade.pool.hex()}")
	print(f"  Expiration: {trade.expiration}")
	print(f"  Salt: {trade.salt}")
	print(f"  Maker Is Buyer: {trade.makerIsBuyer}")

if len(settlement_ready_trades) > 5:
	print("\n... (remaining trades omitted for brevity)")
