import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OrderMatchingEngine import Order, Orderbook, Side, LimitOrder
from OrderMatchingEngine.PackagerV2 import create_settlement_ready_trades, serialize_settlement_ready_trades
from random import getrandbits, randint
import json
import secrets

def create_random_signature():
    signature_type = 'EIP-712'
    v = randint(27, 28)  # v is typically 27 or 28 for Ethereum signatures
    r = secrets.token_bytes(32)  # 32 bytes for r
    s = secrets.token_bytes(32)  # 32 bytes for s
    return signature_type, v, r, s

def test_serialization():
    # Create an orderbook and populate it with random orders
    OB = Orderbook()
    numOrders = 10  # Reduced number of orders for quicker testing
    orders = []
    for n in range(numOrders):
        side = Side.BUY if bool(getrandbits(1)) else Side.SELL
        size = randint(1, 200)
        price = randint(1, 4)
        signature_type, v, r, s = create_random_signature()
        
        order = LimitOrder(n, side, size, price)
        order.set_signature(signature_type, v, r, s)
        orders.append(order)

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
