from web3 import Web3
from eth_account import Account
import json
import os

# Connect to your network (e.g., local Anvil)
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

# Load contract ABIs
with open('out/ConcreteNativeOrdersSettlement.sol/ConcreteNativeOrdersSettlement.json') as f:
    settlement_abi = json.load(f)['abi']

with open('out/TestERC20.sol/TestERC20.json') as f:
    token_abi = json.load(f)['abi']

# Contract addresses from deployment
SETTLEMENT_ADDRESS = "0x..." # Get from deployment
CASH_TOKEN_ADDRESS = "0x..."  # Get from deployment
SECURITY_TOKEN_ADDRESS = "0x..."  # Get from deployment

# Initialize contracts
settlement = w3.eth.contract(address=SETTLEMENT_ADDRESS, abi=settlement_abi)
cash_token = w3.eth.contract(address=CASH_TOKEN_ADDRESS, abi=token_abi)
security_token = w3.eth.contract(address=SECURITY_TOKEN_ADDRESS, abi=token_abi)

def submit_trade(trade):
    # Convert trade data to contract format
    limit_order = {
        'makerToken': trade['makerToken'],
        'takerToken': trade['takerToken'],
        'makerAmount': int(trade['makerAmount']),
        'takerAmount': int(trade['takerAmount']),
        'protocolFeeAmount': 0,
        'maker': trade['maker'],
        'taker': trade['taker'],
        'sender': trade['sender'],
        'feeRecipient': trade['feeRecipient'],
        'pool': trade['pool'],
        'expiry': int(trade['expiration']),
        'salt': int(trade['salt']),
        'makerIsBuyer': trade['makerIsBuyer']
    }

    signatures = {
        'signatureType': 2,  # EIP712
        'maker_v': trade['maker_v'],
        'maker_r': trade['maker_r'],
        'maker_s': trade['maker_s'],
        'taker_v': trade['taker_v'],
        'taker_r': trade['taker_r'],
        'taker_s': trade['taker_s']
    }

    # Build transaction
    tx = settlement.functions.fillLimitOrder(
        limit_order,
        signatures,
        int(trade['takerAmount'])  # takerTokenFillAmount
    ).build_transaction({
        'from': w3.eth.accounts[0],
        'gas': 500000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
    })

    # Sign and send transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='your_private_key')
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def main():
    # Load trades from packaged_trades.json
    with open('../Order-Book-Matching-Engine/OrderMatchingEngine/packaged_trades.json') as f:
        trades = json.load(f)

    # Submit each trade
    for i, trade in enumerate(trades):
        print(f"Submitting trade {i}...")
        receipt = submit_trade(trade)
        print(f"Trade {i} settled in tx: {receipt.transactionHash.hex()}")

if __name__ == "__main__":
    main()