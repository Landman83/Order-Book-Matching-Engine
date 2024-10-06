from OrderMatchingEngine.Order import *
from time import time
import secrets

class Trade(object):
	"""
	Trade
	-----

	A trade object
	"""
	def __init__(self, incoming_order_id, book_order_id, incoming_side, price, size, buyer_id, seller_id):
		self.incoming_order_id = incoming_order_id
		self.book_order_id = book_order_id
		self.incoming_side = incoming_side
		self.price = price
		self.size = size
		self.buyer_id = buyer_id
		self.seller_id = seller_id

	def __repr__(self):
		return (f"Trade: Incoming Order ID: {self.incoming_order_id}, Book Order ID: {self.book_order_id}, "
				f"Incoming Side: {self.incoming_side}, Price: {self.price}, Size: {self.size}, "
				f"Buyer ID: {self.buyer_id}, Seller ID: {self.seller_id}")