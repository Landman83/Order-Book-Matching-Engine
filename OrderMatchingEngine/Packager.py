## This file is used to translate the matched orders into a format which can be used by the settlement engine
import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from OrderMatchingEngine.Orderbook import Orderbook
from OrderMatchingEngine.Trade import Trade
from OrderMatchingEngine import Side

class SettleableMatchedOrder:
    def __init__(self, cashAmount, securityAmount, buyer, seller, cashToken, securityToken, maker, taker):
        self.cashAmount = cashAmount
        self.securityAmount = securityAmount
        self.buyer = buyer
        self.seller = seller
        self.cashToken = cashToken
        self.securityToken = securityToken
        self.maker = maker
        self.taker = taker

def create_settleable_matched_orders(orderbook, cash_token, security_token):
    settleable_orders = []
    
    for trade in orderbook.trades:
        cash_amount = trade.price * trade.size
        security_amount = trade.size
        buyer = trade.buyer_id
        seller = trade.seller_id
        
        if trade.incoming_side == Side.SELL:
            maker = buyer
            taker = seller
        else:  # BUY
            maker = seller
            taker = buyer
        
        settleable_order = SettleableMatchedOrder(
            cashAmount=cash_amount,
            securityAmount=security_amount,
            buyer=buyer,
            seller=seller,
            cashToken=cash_token,
            securityToken=security_token,
            maker=maker,
            taker=taker
        )
        
        settleable_orders.append(settleable_order)
    
    return settleable_orders

# Example usage:
orderbook = Orderbook()
# ... populate orderbook with orders and execute trades ...

# Set Ethereum addresses for tokens
cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token

settleable_orders = create_settleable_matched_orders(orderbook, cash_token, security_token)

# Print the settleable orders
for i, order in enumerate(settleable_orders, 1):
    print(f"Settleable Order {i}:")
    print(f"  Cash Amount: {order.cashAmount}")
    print(f"  Security Amount: {order.securityAmount}")
    print(f"  Buyer: {order.buyer}")
    print(f"  Seller: {order.seller}")
    print(f"  Cash Token: {order.cashToken}")
    print(f"  Security Token: {order.securityToken}")
    print(f"  Maker: {order.maker}")
    print(f"  Taker: {order.taker}")
    print()

