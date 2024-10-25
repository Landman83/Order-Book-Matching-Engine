import json
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OrderMatchingEngine.Orderbook import Orderbook
from OrderMatchingEngine.Order import LimitOrder, Side
from OrderMatchingEngine.PackagerV3 import create_settlement_ready_trades, serialize_settlement_ready_trades

def load_orders_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def convert_to_limit_order(order_data):
    side = Side.BUY if order_data['side'] == 1 else Side.SELL
    order = LimitOrder(
        order_id=order_data['orderId'],
        side=side,
        size=order_data['size'],
        price=order_data['price'],
        trader_id=order_data['trader']
    )
    # Add signature data
    order.signature_type = order_data['signatureType']
    order.v = order_data['v']
    order.r = order_data['r']
    order.s = order_data['s']
    return order

def ingest_orders(orderbook, filename):
    orders_data = load_orders_from_file(filename)
    print(f"Total orders loaded: {len(orders_data)}")
    buy_orders = 0
    sell_orders = 0
    for order_data in orders_data:
        order = convert_to_limit_order(order_data)
        if order.side == Side.BUY:
            buy_orders += 1
        else:
            sell_orders += 1
        orderbook.add_order(order)
    print(f"Buy orders: {buy_orders}, Sell orders: {sell_orders}")

def package_trades(trades, cash_token, security_token, fee_recipient):
    settlement_ready_trades = create_settlement_ready_trades(trades, cash_token, security_token, fee_recipient)
    return serialize_settlement_ready_trades(settlement_ready_trades)

def print_orderbook_summary(orderbook):
    print("Current Orderbook State:")
    print("------------------------")
    print(f"Total asks: {len(orderbook.asks)}")
    print(f"Total bids: {len(orderbook.bids)}")
    print("5 Lowest Asks:")
    for ask in sorted(orderbook.asks)[:5]:
        print(f"  Price: {ask.price}, Size: {ask.size}, Order ID: {ask.order_id}")
    print("\n5 Highest Bids:")
    for bid in sorted(orderbook.bids, reverse=True)[:5]:
        print(f"  Price: {bid.price}, Size: {bid.size}, Order ID: {bid.order_id}")
    print("------------------------")

def print_matched_trades(trades):
    print("\nMatched Trades:")
    print("---------------")
    if not trades:
        print("No matched trades.")
    else:
        for i, trade in enumerate(trades, 1):
            print(f"Trade {i}:")
            print(f"  Buyer ID: {trade.buyer_id}")
            print(f"  Seller ID: {trade.seller_id}")
            print(f"  Price: {trade.price}")
            print(f"  Size: {trade.size}")
            print("---------------")

def print_packaged_trade(packaged_trade):
    print(f"Packaged Trade:")
    print(json.dumps(packaged_trade, indent=2))
    print("-" * 50)

def main():
    # Initialize the orderbook
    orderbook = Orderbook()

    # Ingest orders from the JSON file
    ingest_orders(orderbook, '../../orderCreation/test_orders.json')

    # Print the current state of the orderbook
    print_orderbook_summary(orderbook)

    # Print all matched trades
    print_matched_trades(orderbook.trades)

    # Set Ethereum addresses for tokens and fee recipient (you may want to make these configurable)
    cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
    security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token
    fee_recipient = "0xfedc000000000000000000000000000000000000"  # Example Ethereum address for fee recipient

    # Add this debug print
    print(f"Number of trades: {len(orderbook.trades)}")

    # Package the trades
    packaged_trades = package_trades(orderbook.trades, cash_token, security_token, fee_recipient)

    # Add this debug print
    print(f"Number of packaged trades: {len(packaged_trades)}")

    # Print the packaged trades
    print("\nPackaged Trades:")
    for packaged_trade in packaged_trades:
        print_packaged_trade(packaged_trade)

if __name__ == "__main__":
    main()
