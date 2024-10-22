import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OrderMatchingEngine import Order, Orderbook, Side, LimitOrder
from OrderMatchingEngine.PackagerV2 import create_settlement_ready_trades, serialize_settlement_ready_trades
from random import getrandbits, randint
import json

def test_serialization():
    # Create an orderbook and populate it with random orders
    OB = Orderbook()
    numOrders = 10  # Reduced number of orders for quicker testing
    orders = []
    for n in range(numOrders):
        if bool(getrandbits(1)):
            orders.append(LimitOrder(n, Side.BUY, randint(1, 200), randint(1, 4)))
        else:
            orders.append(LimitOrder(n, Side.SELL, randint(1, 200), randint(1, 4)))

    # Process the orders
    for order in orders:
        OB.processOrder(order)

    # Create Settlement Ready Trades
    cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
    security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token
    fee_recipient = "0xfedc000000000000000000000000000000000000"  # Example Ethereum address for fee recipient

    settlement_ready_trades = create_settlement_ready_trades(OB, cash_token, security_token, fee_recipient)

    # Serialize the settlement ready trades
    serialized_trades = serialize_settlement_ready_trades(settlement_ready_trades)

    # Print the total number of serialized trades
    print(f"Total Serialized Trades: {len(serialized_trades)}")

    # Print the first 5 serialized trades (or all if less than 5)
    print("\nFirst 5 Serialized Trades:")
    print(json.dumps(serialized_trades[:5], indent=2))

    if len(serialized_trades) > 5:
        print("\n... (remaining trades omitted for brevity)")

    # Optionally, save all serialized trades to a file
    with open('test_serialized_trades.json', 'w') as f:
        json.dump(serialized_trades, f, indent=2)
    print("\nAll serialized trades have been saved to 'test_serialized_trades.json'")

if __name__ == "__main__":
    test_serialization()

