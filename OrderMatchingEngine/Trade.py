from OrderMatchingEngine.Order import *
from time import time
import secrets

class Trade(object):
	"""
	Trade
	-----

	A trade object
	"""
	def __init__(self, maker_order_id, taker_order_id, price, size, buyer_id, seller_id,
				 signature_type, v_maker, r_maker, s_maker, v_taker, r_taker, s_taker):
		self.maker_order_id = maker_order_id
		self.taker_order_id = taker_order_id
		self.price = price
		self.size = size
		self.buyer_id = buyer_id
		self.seller_id = seller_id
		self.signature_type = signature_type
		self.v_maker = v_maker
		self.r_maker = r_maker
		self.s_maker = s_maker
		self.v_taker = v_taker
		self.r_taker = r_taker
		self.s_taker = s_taker

	def __repr__(self):
		return (f"Trade: Maker Order ID: {self.maker_order_id}, Taker Order ID: {self.taker_order_id}, "
				f"Price: {self.price}, Size: {self.size}, "
				f"Buyer ID: {self.buyer_id}, Seller ID: {self.seller_id}, "
				f"Signature Type: {self.signature_type}")
