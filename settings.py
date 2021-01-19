import time
from web3 import Web3
from decimal import Decimal

# tx sender
address_tx_sender = Web3.toChecksumAddress("own_address")

# uniswap/sushi router合约地址
address_router_contract = Web3.toChecksumAddress("0x7a250d5630b4cf539739df2c5dacb4c659f2488d")

# uniswap/sushi factory合约地址
address_factory_contract = Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")

basicTokensAddress = {
    "weth": {
      "mainnet": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
      "local": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
      "ropsten": "0xc778417E063141139Fce010982780140Aa0cD5Ab",
      "kovan": "0xd0A1E359811322d97991E03f863a0C30C2cF029C"
      },
    "usdt": {
      "mainnet": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      "local": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
      "ropsten": "",
      "kovan": ""
      },
    "usdc": {
      "mainnet": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "local": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "ropsten": "",
      "kovan": "0xe22da380ee6B445bb8273C81944ADEB6E8450422"
      },
    "dai": {
      "mainnet": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
      "local": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
      "ropsten": "0xaD6D458402F60fD3Bd25163575031ACDce07538D",
      "kovan": "0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD"
      },
    }


network = "mainnet"

weth = basicTokensAddress["weth"][network]
usdt = basicTokensAddress["usdt"][network]
usdc = basicTokensAddress["usdc"][network]
dai  = basicTokensAddress["dai"][network]

basicTokens = {
        'weth': {
            'address': weth,
            'symbol': 'WETH',
            'decimal': 18,
            },
        'usdt': {
                'address': usdt,
                'symbol': 'USDT',
                'decimal': 6,
                },
        'usdc': {
                'address': usdc,
                'symbol': 'USDC',
                'decimal': 6,
                },
        'dai': {
                'address': dai,
                'symbol': 'DAI',
                'decimal': 18,
                },
        }

maxHops = 6
startToken = basicTokens["weth"]
minProfit = 0.01
slidePoint = 0.05
gasPrice = 200*10**9    # 200 Gwei
reserveMinAmount = 10

ethereum_http = "own_ethereum_node"

class ProgramStatus(object):
    def __init__(self, running=True):
        self.__running = running

    def running(self):
        return self.__running

    def setRuning(self, running:bool):
        self.__running = running

programStatus = ProgramStatus()

def timer():
    last_time = Decimal(str(time.time()))
    while 1:
        current_time = Decimal(str(time.time()))
        d = current_time - last_time
        last_time = current_time
        yield d
