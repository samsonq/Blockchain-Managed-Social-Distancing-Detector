import json
from web3 import Web3


address = ""
contract_abi = ""
infura = "https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"


class OnChain:

    def __init__(self, bin, abi=contract_abi, provider=infura):
        self.web3 = Web3(Web3.HTTPProvider(provider))
        self.abi = abi
        self.bin = bin

