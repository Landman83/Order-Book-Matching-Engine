from enum import Enum
from time import time
import secrets

class Side(Enum):
    BUY = 0
    SELL = 1

class Order(object):
    def __init__(self, order_id: int, side: Side, price=None, size=None, trader_id=None, signature_type='EIP-712', v=None, r=None, s=None):
        self.order_id = order_id
        self.side = side
        self.price = price
        self.size = size
        self.remainingToFill = size
        self.trader_id = trader_id
        self.time = int(1e6 * time())
        self.signature_type = signature_type
        self.v = v
        self.r = r
        self.s = s
    
    def __getType__(self):
        return self.__class__

    def set_signature(self, signature_type, v, r, s):
        self.signature_type = signature_type
        self.v = v
        self.r = r
        self.s = s

    def __repr__(self):
        return f"Order(id={self.order_id}, side={self.side}, price={self.price}, size={self.size}, remaining={self.remainingToFill})"


class CancelOrder(Order):
    def __init__(self, order_id):
        super().__init__(order_id)

    def __repr__(self):
        return "Cancel Order: {}.".format(self.order_id)


class MarketOrder(Order):
    def __init__(self, order_id: int, side: Side, size: int, trader_id=None, signature_type='EIP-712', v=None, r=None, s=None):
        super().__init__(order_id, side, None, size, trader_id, signature_type, v, r, s)
        self.side = side
        self.size = self.remainingToFill = size
    
    def __repr__(self):
        return "Market Order: {0} {1} units.".format(
            "BUY" if self.side == Side.BUY else "SELL",
            self.remainingToFill)


class LimitOrder(MarketOrder):
    def __init__(self, order_id: int, side: Side, size: int, price: int, trader_id=None, signature_type='EIP-712', v=None, r=None, s=None):
        super().__init__(order_id, side, size, trader_id, signature_type, v, r, s)
        self.price = price
    
    def __lt__(self, other):
        if self.price != other.price:
            if self.side == Side.BUY:
                return self.price > other.price
            else:
                return self.price < other.price
        elif self.time != other.time:
             return self.time < other.time
        elif self.size != other.size:
            return self.size < other.size

    def __repr__(self):
        return 'Limit Order: {0} {1} units at {2}.'.format(
            "BUY" if self.side == Side.BUY else "SELL",
            self.remainingToFill, self.price)
