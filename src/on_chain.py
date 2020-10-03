import json
from web3 import Web3
from hashlib import sha256


address = ""
contract_abi = ""
infura = "https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"


class OnChain:

    def __init__(self, bin, abi=contract_abi, provider=infura):
        self.web3 = Web3(Web3.HTTPProvider(provider))
        self.abi = abi
        self.bin = bin

    @staticmethod
    def sha256_hash(event_id, location, time, violations):
        """
        Performs SHA256 hash to generate a string output.
        :return: hash of inputs
        """
        event_str = event_id + location + time + violations
        return sha256(event_str.encode()).hexdigest()

    def store_hash(self, event_id, location, time, violations):
        """
        Stores event-generated hash on-chain.
        :param event_id:
        :param location:
        :param time:
        :param violations:
        :return:
        """
        event_hash = self.sha256_hash(event_id, location, time, violations)
        ...
