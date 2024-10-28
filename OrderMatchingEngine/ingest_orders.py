import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OrderMatchingEngine.Orderbook import Orderbook
from OrderMatchingEngine.Order import LimitOrder, Side
from OrderMatchingEngine.PackagerV2 import create_settlement_ready_trades, serialize_settlement_ready_trades

def load_orders_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def convert_to_limit_order(order_data):
    side = Side.BUY if order_data['side'] == 0 else Side.SELL
    return LimitOrder(
        order_id=order_data['orderId'],
        side=side,
        size=order_data['size'],
        price=order_data['price'],
        trader_id=order_data['trader'],
        signature_type=order_data['signatureType'],
        v=order_data['v'],
        r=order_data['r'],
        s=order_data['s']
    )

def main():
    # Initialize the orderbook
    orderbook = Orderbook()

    # Load orders from the JSON file
    orders_data = load_orders_from_file('../../orderCreation/test_orders.json')

    # Process each order through the orderbook
    for order_data in orders_data:
        order = convert_to_limit_order(order_data)
        orderbook.add_order(order)

    # Print summary of processed orders
    print(f"Processed {len(orders_data)} orders")
    print(f"Resulting in {len(orderbook.trades)} trades")

    # Set fee recipient
    fee_recipient = "0x3C44CdddB6a900fa2b585dd299e03d12FA4293BC"

    # Package the trades - only pass trades and fee_recipient
    settlement_ready_trades = create_settlement_ready_trades(orderbook.trades, fee_recipient)
    packaged_trades = serialize_settlement_ready_trades(settlement_ready_trades)

    # Print the packaged trades
    print("\nPackaged Trades:")
    print(json.dumps(packaged_trades, indent=2))

    # Optionally, save the packaged trades to a file
    with open('packaged_trades.json', 'w') as f:
        json.dump(packaged_trades, f, indent=2)

if __name__ == "__main__":
    main()
