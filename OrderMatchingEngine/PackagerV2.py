## This file is used to translate the matched orders into a format which can be used by the settlement engine
import sys
import os
from eth_utils import to_checksum_address
from web3 import Web3
import time
import json

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

def create_settlement_ready_trades(orderbook, cash_token, security_token, fee_recipient):
    settlement_ready_trades = []
    
    for trade in orderbook.trades:
        cash_amount = int(trade.price * trade.size)  # Convert to integer
        security_amount = int(trade.size)  # Convert to integer
        
        # Determine makerIsBuyer based on incoming side
        maker_is_buyer = trade.incoming_side != Side.BUY
        
        # Set maker and taker based on makerIsBuyer
        if maker_is_buyer:
            maker = to_checksum_address(trade.buyer_id)
            taker = to_checksum_address(trade.seller_id)
        else:
            maker = to_checksum_address(trade.seller_id)
            taker = to_checksum_address(trade.buyer_id)
        
        # Set maker and taker tokens based on makerIsBuyer
        if maker_is_buyer:
            maker_token = cash_token
            taker_token = security_token
            maker_amount = cash_amount
            taker_amount = security_amount
        else:
            maker_token = security_token
            taker_token = cash_token
            maker_amount = security_amount
            taker_amount = cash_amount
        
        settlement_ready_trade = SettlementReadyTrade(
            makerToken=maker_token,
            takerToken=taker_token,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            maker=maker,
            taker=taker,
            sender=Web3.to_checksum_address('0x0000000000000000000000000000000000000000'),  # Zero address
            feeRecipient=to_checksum_address(fee_recipient),
            pool=Web3.to_bytes(hexstr='0x0000000000000000000000000000000000000000000000000000000000000000'),  # Zero bytes32
            expiration=int(time.time()) + 3600,  # Current time + 1 hour
            salt=Web3.to_int(Web3.keccak(text=str(time.time()))),  # Unique salt based on current time
            makerIsBuyer=maker_is_buyer,
            signature_type=trade.signature_type,
            buyer_v=trade.v_buyer,
            buyer_r=trade.r_buyer,
            buyer_s=trade.s_buyer,
            seller_v=trade.v_seller,
            seller_r=trade.r_seller,
            seller_s=trade.s_seller
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
    orderbook = Orderbook()
    # ... populate orderbook with orders and execute trades ...

    # Set Ethereum addresses for tokens and fee recipient
    cash_token = "0x1234567890123456789012345678901234567890"  # Example Ethereum address for cash token
    security_token = "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"  # Example Ethereum address for security token
    fee_recipient = "0xfedc000000000000000000000000000000000000"  # Example Ethereum address for fee recipient

    settlement_ready_trades = create_settlement_ready_trades(orderbook, cash_token, security_token, fee_recipient)

    # Serialize the settlement ready trades
    serialized_trades = serialize_settlement_ready_trades(settlement_ready_trades)

    # Print the serialized trades
    print(json.dumps(serialized_trades, indent=2))

    # Optionally, save the serialized trades to a file
    with open('settlement_ready_trades.json', 'w') as f:
        json.dump(serialized_trades, f, indent=2)
