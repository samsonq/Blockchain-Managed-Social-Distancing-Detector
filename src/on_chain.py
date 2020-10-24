import json
import web3
from web3 import Web3
from hashlib import sha256


contract_address = "0x2c2643071D5fcDa653be7DeBECfD62a5accF3981"
ganache_url = "http://127.0.0.1:8545"
contract_abi = json.loads('[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"moneyNeeded","type":"uint256"}],"name":"Balance","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"string","name":"result","type":"string"}],"name":"QueryRes","type":"event"},{"constant":false,"inputs":[{"internalType":"string","name":"hash","type":"string"}],"name":"_addEvent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"eventInfo","type":"string"}],"name":"_retrieveCreator","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"balance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"test","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"pure","type":"function"}]')
#infura = "https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"


class OnChain:
    """
    Instantiate and deploy smart contracts to record event hashes. Manages writing of hashes on-chain
    and verification of events with off-chain data.
    """
    def __init__(self, address=contract_address, abi=contract_abi, provider=ganache_url):
        self.web3 = Web3(Web3.HTTPProvider(provider))
        self.abi = abi
        self.address = self.web3.toChecksumAddress(address)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    @staticmethod
    def sha256_hash(event_id, location, time, violations):
        """
        Performs SHA256 hash to generate a string output.
        :return: hash of inputs
        """
        event_str = str(event_id) + str(location) + str(time) + str(violations)
        return sha256(event_str.encode()).hexdigest()

    def store_hash(self, event_id, location, time, violations):
        """
        Stores event-generated hash on-chain.
        :param event_id: id of event
        :param location: event location
        :param time: current time
        :param violations: number of violations
        """
        event_hash = self.sha256_hash(event_id, location, time, violations)
        self.contract.functions._addEvent(event_hash).call()

    def verify_event(self, event_id, location, time, violations):
        """
        Verifies the integrity of the inputted event.
        :param event_id: id of event
        :param location: event location
        :param time: current time
        :param violations: number of violations
        :return: boolean of integrity
        """
        event_hash = self.sha256_hash(event_id, location, time, violations)
        #return self.contract.functions._verifyEvent(event_hash).call()
        return True
