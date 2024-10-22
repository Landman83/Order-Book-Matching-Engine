from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_structured_data
from typing import Dict, Optional
import time
import secrets
from enum import Enum

from OrderMatchingEngine.Order import Side, LimitOrder, MarketOrder
from OrderMatchingEngine.Orderbook import Orderbook

class OrderCreator:
    def __init__(self, web3_provider: str, chain_id: int, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
        # EIP-712 domain
        self.domain = {
            'name': 'DEX Protocol',
            'version': '1',
            'chainId': chain_id,
            'verifyingContract': contract_address
        }
        
        self.order_types = {
            'Order': [
                {'name': 'trader', 'type': 'address'},
                {'name': 'side', 'type': 'uint8'},
                {'name': 'price', 'type': 'uint256'},
                {'name': 'size', 'type': 'uint256'},
                {'name': 'nonce', 'type': 'uint256'},
                {'name': 'expiration', 'type': 'uint256'}
            ]
        }

    def create_order(
        self,
        trader_address: str,
        side: Side,
        size: int,
        price: Optional[int] = None,
        expiration_hours: int = 24,
        private_key: str = None
    ) -> Dict:
        order_id = secrets.randbelow(1000000)  # Generate a random order ID
        
        order = {
            'trader': trader_address,
            'side': side.value,
            'price': price if price is not None else 0,
            'size': size,
            'nonce': self.w3.eth.get_transaction_count(trader_address),
            'expiration': int(time.time()) + (expiration_hours * 3600)
        }

        if private_key:
            signature = self._sign_order(order, private_key)
            signature_type, v, r, s = self._split_signature(signature)
        else:
            signature_type, v, r, s = None, None, None, None

        if price is None:
            return MarketOrder(order_id, side, size)
        else:
            limit_order = LimitOrder(order_id, side, size, price)
            limit_order.signature_type = signature_type
            limit_order.v = v
            limit_order.r = r
            limit_order.s = s
            return limit_order

    def _sign_order(self, order: Dict, private_key: str) -> str:
        structured_data = {
            'domain': self.domain,
            'message': order,
            'primaryType': 'Order',
            'types': self.order_types
        }
        signed_message = Account.from_key(private_key).sign_message(
            encode_structured_data(structured_data)
        )
        return signed_message.signature.hex()

    def _split_signature(self, signature: str):
        signature_bytes = bytes.fromhex(signature[2:])  # Remove '0x' prefix
        return (
            int(signature_bytes[0]),  # signature_type (v[0])
            int(signature_bytes[1]),  # v
            signature_bytes[2:34],    # r
            signature_bytes[34:66]    # s
        )

def main():
    creator = OrderCreator(
        web3_provider='YOUR_NODE_URL',
        chain_id=1,  # Mainnet
        contract_address='0x123...'
    )
    
    orderbook = Orderbook()

    while True:
        print("\n1. Create Market Order")
        print("2. Create Limit Order")
        print("3. View Orderbook")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            side = Side.BUY if input("Enter side (buy/sell): ").lower() == 'buy' else Side.SELL
            size = int(input("Enter size: "))
            order = creator.create_order(
                trader_address='0x' + secrets.token_hex(20),
                side=side,
                size=size
            )
            orderbook.processOrder(order)
            print(f"Market Order created and processed: {order}")

        elif choice == '2':
            side = Side.BUY if input("Enter side (buy/sell): ").lower() == 'buy' else Side.SELL
            size = int(input("Enter size: "))
            price = int(input("Enter price: "))
            order = creator.create_order(
                trader_address='0x' + secrets.token_hex(20),
                side=side,
                size=size,
                price=price,
                private_key='0x' + secrets.token_hex(32)  # Generate a random private key
            )
            orderbook.processOrder(order)
            print(f"Limit Order created and processed: {order}")

        elif choice == '3':
            print(orderbook)

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

    print("Exiting program.")

if __name__ == "__main__":
    main()
