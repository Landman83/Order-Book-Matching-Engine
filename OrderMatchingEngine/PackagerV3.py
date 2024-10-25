## This file is used to translate the matched orders into a format which can be used by the settlement engine
import sys
import os
from eth_utils import to_checksum_address
from web3 import Web3
import time
import json
import random

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from OrderMatchingEngine.Orderbook import Orderbook
from OrderMatchingEngine.Trade import Trade
from OrderMatchingEngine import Side

class SettlementReadyTrade:
    def __init__(self, makerToken, takerToken, makerAmount, takerAmount, maker, taker, sender, feeRecipient, pool, expiration, salt, makerIsBuyer, signature_type, buyer_v, buyer_r, buyer_s, seller_v, seller_r, seller_s):
        self.makerToken = makerToken
        self.takerToken = takerToken
        self.makerAmount = makerAmount
        self.takerAmount = takerAmount
        self.maker = maker
        self.taker = taker
        self.sender = sender
        self.feeRecipient = feeRecipient
        self.pool = pool
        self.expiration = expiration
        self.salt = salt
        self.makerIsBuyer = makerIsBuyer
        self.signature_type = signature_type
        self.buyer_v = buyer_v
        self.buyer_r = buyer_r
        self.buyer_s = buyer_s
        self.seller_v = seller_v
        self.seller_r = seller_r
        self.seller_s = seller_s

def create_settlement_ready_trades(trades, cash_token, security_token, fee_recipient):
    settlement_ready_trades = []
    
    for trade in trades:
        cash_amount = int(trade.price * trade.size)
        security_amount = int(trade.size)
        
        maker_is_buyer = trade.buyer_id < trade.seller_id
        
        if maker_is_buyer:
            maker = Web3.to_checksum_address(trade.buyer_id)
            taker = Web3.to_checksum_address(trade.seller_id)
            maker_token = Web3.to_checksum_address(security_token)
            taker_token = Web3.to_checksum_address(cash_token)
            maker_amount = security_amount
            taker_amount = cash_amount
        else:
            maker = Web3.to_checksum_address(trade.seller_id)
            taker = Web3.to_checksum_address(trade.buyer_id)
            maker_token = Web3.to_checksum_address(cash_token)
            taker_token = Web3.to_checksum_address(security_token)
            maker_amount = cash_amount
            taker_amount = security_amount

        salt = Web3.keccak(text=f"{maker}{taker}{time.time()}{random.random()}").hex()

        settlement_ready_trade = SettlementReadyTrade(
            makerToken=maker_token,
            takerToken=taker_token,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            maker=maker,
            taker=taker,
            sender=taker,
            feeRecipient=Web3.to_checksum_address(fee_recipient),
            pool=Web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
            expiration=Web3.to_hex(int(time.time()) + 3600),
            salt=salt,
            makerIsBuyer=maker_is_buyer,
            signature_type="EIP-712",  # Assuming EIP-712 signatures
            buyer_v=0,  # Placeholder, adjust if you have this information
            buyer_r=b'',  # Placeholder, adjust if you have this information
            buyer_s=b'',  # Placeholder, adjust if you have this information
            seller_v=0,  # Placeholder, adjust if you have this information
            seller_r=b'',  # Placeholder, adjust if you have this information
            seller_s=b''  # Placeholder, adjust if you have this information
        )
        
        settlement_ready_trades.append(settlement_ready_trade)
    
    return settlement_ready_trades

def serialize_trade(trade):
    return {
        "makerToken": trade.makerToken,
        "takerToken": trade.takerToken,
        "makerAmount": str(trade.makerAmount),
        "takerAmount": str(trade.takerAmount),
        "maker": trade.maker,
        "taker": trade.taker,
        "sender": trade.sender,
        "feeRecipient": trade.feeRecipient,
        "pool": trade.pool.hex(),
        "expiration": trade.expiration,
        "salt": str(trade.salt),
        "makerIsBuyer": trade.makerIsBuyer,
        "signature_type": trade.signature_type,
        "buyer_v": trade.buyer_v,
        "buyer_r": '0x' + trade.buyer_r.hex() if trade.buyer_r else None,
        "buyer_s": '0x' + trade.buyer_s.hex() if trade.buyer_s else None,
        "seller_v": trade.seller_v,
        "seller_r": '0x' + trade.seller_r.hex() if trade.seller_r else None,
        "seller_s": '0x' + trade.seller_s.hex() if trade.seller_s else None
    }

def serialize_settlement_ready_trades(settlement_ready_trades):
    return [serialize_trade(trade) for trade in settlement_ready_trades]

# Example usage:
if __name__ == "__main__":
    # Assume we have a list of trades instead of an Orderbook
    trades = []  # You would populate this with actual Trade objects

    # Set Ethereum addresses for tokens and fee recipient
    cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
    security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token
    fee_recipient = "0xfedc000000000000000000000000000000000000"  # Example Ethereum address for fee recipient

    settlement_ready_trades = create_settlement_ready_trades(trades, cash_token, security_token, fee_recipient)

    # Serialize the settlement ready trades
    serialized_trades = serialize_settlement_ready_trades(settlement_ready_trades)

    # Print the serialized trades
    print(json.dumps(serialized_trades, indent=2))

    # Optionally, save the serialized trades to a file
    with open('settlement_ready_trades.json', 'w') as f:
        json.dump(serialized_trades, f, indent=2)
