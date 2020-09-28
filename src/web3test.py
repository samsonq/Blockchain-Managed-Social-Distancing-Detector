from web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/7fc9b313b47d488c97c52c3221344c04"))
print(web3.eth.blockNumber)