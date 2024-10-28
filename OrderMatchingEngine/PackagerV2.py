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

# Token addresses
CASH_TOKEN_ADDRESS = "0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f"
SECURITY_TOKEN_ADDRESS = "0x2e234DAe75C793f67A35089C9d99245E1C58470b"
FEE_RECIPIENT = "0x3C44CdddB6a900fa2b585dd299e03d12FA4293BC"

class SettlementReadyTrade:
    def __init__(self, makerToken, takerToken, makerAmount, takerAmount, maker, taker, sender, feeRecipient, pool, expiration, salt, makerIsBuyer, signature_type, maker_v, maker_r, maker_s, taker_v, taker_r, taker_s):
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
        self.maker_v = maker_v
        self.maker_r = maker_r
        self.maker_s = maker_s
        self.taker_v = taker_v
        self.taker_r = taker_r
        self.taker_s = taker_s

def create_settlement_ready_trades(trades, fee_recipient):
    settlement_ready_trades = []
    
    for trade in trades:
        cash_amount = int(trade.price * trade.size)
        security_amount = int(trade.size)
        
        # Determine maker and taker based on order IDs
        # The maker is always the one with the lower order ID
        if trade.buyer_id == trade.maker_order_id:
            maker_is_buyer = True
            maker = trade.buyer_id
            taker = trade.seller_id
            maker_token = CASH_TOKEN_ADDRESS
            taker_token = SECURITY_TOKEN_ADDRESS
            maker_amount = cash_amount
            taker_amount = security_amount
        else:
            maker_is_buyer = False
            maker = trade.seller_id
            taker = trade.buyer_id
            maker_token = SECURITY_TOKEN_ADDRESS
            taker_token = CASH_TOKEN_ADDRESS
            maker_amount = security_amount
            taker_amount = cash_amount
        
        settlement_ready_trade = SettlementReadyTrade(
            makerToken=maker_token,
            takerToken=taker_token,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            maker=maker,
            taker=taker,
            sender=Web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
            feeRecipient=to_checksum_address(fee_recipient),
            pool=Web3.to_bytes(hexstr='0x0000000000000000000000000000000000000000000000000000000000000000'),
            expiration=int(time.time()) + 3600,
            salt=Web3.to_int(Web3.keccak(text=str(time.time()))),
            makerIsBuyer=maker_is_buyer,
            signature_type=trade.signature_type,
            maker_v=trade.v_maker,
            maker_r=trade.r_maker,
            maker_s=trade.s_maker,
            taker_v=trade.v_taker,
            taker_r=trade.r_taker,
            taker_s=trade.s_taker
        )
        
        settlement_ready_trades.append(settlement_ready_trade)
    
    return settlement_ready_trades

def serialize_trade(trade):
    def format_hex(value):
        if isinstance(value, bytes):
            return '0x' + value.hex()
        elif isinstance(value, str):
            return value if value.startswith('0x') else '0x' + value
        else:
            return None

    return {
        "makerToken": trade.makerToken,
        "takerToken": trade.takerToken,
        "makerAmount": str(trade.makerAmount),
        "takerAmount": str(trade.takerAmount),
        "maker": trade.maker,
        "taker": trade.taker,
        "sender": trade.sender,
        "feeRecipient": trade.feeRecipient,
        "pool": trade.pool.hex() if isinstance(trade.pool, bytes) else trade.pool,
        "expiration": trade.expiration,
        "salt": str(trade.salt),
        "makerIsBuyer": trade.makerIsBuyer,
        "signature_type": trade.signature_type,
        "maker_v": trade.maker_v,
        "maker_r": format_hex(trade.maker_r),
        "maker_s": format_hex(trade.maker_s),
        "taker_v": trade.taker_v,
        "taker_r": format_hex(trade.taker_r),
        "taker_s": format_hex(trade.taker_s)
    }

def serialize_settlement_ready_trades(settlement_ready_trades):
    return [serialize_trade(trade) for trade in settlement_ready_trades]

def submit_trades_for_settlement(web3, contract_address, contract_abi, trades, account):
    """
    Submit trades to the settlement contract
    
    Args:
        web3: Web3 instance
        contract_address: Settlement contract address
        contract_abi: Settlement contract ABI
        trades: List of serialized trades
        account: Account to submit transactions from
    """
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    transactions = []

    for trade in trades:
        # Create the order object
        order = {
            'makerToken': trade['makerToken'],
            'takerToken': trade['takerToken'],
            'makerAmount': int(trade['makerAmount']),
            'takerAmount': int(trade['takerAmount']),
            'maker': trade['maker'],
            'taker': trade['taker'],
            'sender': trade['sender'],
            'feeRecipient': trade['feeRecipient'],
            'pool': bytes.fromhex(trade['pool']),
            'expiration': trade['expiration'],
            'salt': int(trade['salt']),
            'makerIsBuyer': trade['makerIsBuyer']
        }
        
        # Create the signature object
        signature = {
            'signatureType': trade['signature_type'],
            'maker_v': trade['maker_v'],
            'maker_r': bytes.fromhex(trade['maker_r'][2:]),  # Remove '0x' prefix
            'maker_s': bytes.fromhex(trade['maker_s'][2:]),
            'taker_v': trade['taker_v'],
            'taker_r': bytes.fromhex(trade['taker_r'][2:]),
            'taker_s': bytes.fromhex(trade['taker_s'][2:])
        }
        
        # Build the transaction
        tx = contract.functions.fillLimitOrder(
            order,
            signature,
            int(trade['takerAmount']),  # takerTokenFillAmount
            trade['taker'],             # taker
            trade['sender']             # sender
        ).build_transaction({
            'from': account.address,
            'gas': 300000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(account.address)
        })
        
        transactions.append(tx)
    
    return transactions

# Example usage:
if __name__ == "__main__":
    orderbook = Orderbook()
    # ... populate orderbook with orders and execute trades ...

    # Set Ethereum addresses for tokens and fee recipient
    cash_token = "0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f"  # Example Ethereum address for cash token
    security_token = "0x2e234DAe75C793f67A35089C9d99245E1C58470b"  # Example Ethereum address for security token
    fee_recipient = "0x3C44CdddB6a900fa2b585dd299e03d12FA4293BC"  # Example Ethereum address for fee recipient

    # Assume we have a list of trades instead of an Orderbook
    trades = []  # You would populate this with actual Trade objects
    
    settlement_ready_trades = create_settlement_ready_trades(trades, fee_recipient)

    # Serialize the settlement ready trades
    serialized_trades = serialize_settlement_ready_trades(settlement_ready_trades)

    # Print the serialized trades
    print(json.dumps(serialized_trades, indent=2))

    # Optionally, save the serialized trades to a file
    with open('settlement_ready_trades.json', 'w') as f:
        json.dump(serialized_trades, f, indent=2)

    # Add settlement contract interaction
    try:
        # Load contract ABI
        with open('../order_settlement/artifacts/contracts/core/single_orders/CustomNativeOrderSettlement.sol/NativeOrdersSettlement.json') as f:
            contract_json = json.load(f)
        contract_abi = contract_json['abi']
        
        # Connect to Ethereum node (example using local node)
        w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
        
        # Set up account (you'll need to provide the private key in practice)
        account = w3.eth.account.from_key('YOUR_PRIVATE_KEY')
        
        # Contract address (you'll need to set this after deployment)
        contract_address = 'YOUR_CONTRACT_ADDRESS'
        
        # Create and serialize trades as before
        settlement_ready_trades = create_settlement_ready_trades(trades, fee_recipient)
        serialized_trades = serialize_settlement_ready_trades(settlement_ready_trades)
        
        # Save trades to file
        with open('packaged_trades.json', 'w') as f:
            json.dump(serialized_trades, f, indent=2)
        
        # Submit trades to settlement contract
        transactions = submit_trades_for_settlement(
            w3, 
            contract_address, 
            contract_abi, 
            serialized_trades,
            account
        )
        
        print(f"Generated {len(transactions)} transactions for settlement")
        
        # Optionally, save transactions to file
        with open('settlement_transactions.json', 'w') as f:
            json.dump([tx.hex() for tx in transactions], f, indent=2)

    except Exception as e:
        print(f"Error during settlement: {str(e)}")
