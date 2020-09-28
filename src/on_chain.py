from web3 import Web3


class OnChain:

    def __init__(self, abi, bin, pub, priv, provider="https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"):
        self.web3 = Web3(Web3.HTTPProvider(provider))
        self.abi = abi
        self.bin = bin
        self.pub_key = pub
        self.priv_key = priv

