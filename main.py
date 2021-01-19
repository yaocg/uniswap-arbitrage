import json
import time
import signal
import random
import traceback
from web3 import Web3
from decimal import Decimal
from optparse import OptionParser
from typing import List, Dict, Union

from dfs import findArb
from liquidity import Liquidity
from events import getAmountsOut

from settings import maxHops, startToken
from settings import minProfit
from settings import ethereum_http
from settings import programStatus
from settings import timer
from settings import slidePoint
from settings import gasPrice
from settings import address_router_contract
from settings import address_tx_sender
from settings import reserveMinAmount

from tokens import getWhiteTokens
from pairs import getAllPairInfo
from log_builder import logger
from abi.uniswap_router import abi as router_abi
from contract_fun import estimateGas

class JsonCustomEncoder(json.JSONEncoder):
    def default(self, field):
        if isinstance(field, Decimal):
            return str(field)
        else:
            return json.JSONEncoder.default(self, field)

def randSelect(pairs:List, num:Union[int, None]=None)->List:
    if num is None:
        return pairs

    maxNum = len(pairs)
    start = random.randint(0, maxNum-num)
    return pairs[start:start+num]

def sigint_handler(signum, frame):
    programStatus.setRuning(False)

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGHUP, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)

tokenIn = startToken
tokenOut = tokenIn

tmr = timer()

web3_ins = Web3(Web3.HTTPProvider(ethereum_http))
def main(pairs:List[Dict])->None:
    pairs = randSelect(pairs)
    logger.info(f"pairs num_use: {len(pairs)}")

    next(tmr)
    currentPairs = []
    path = [tokenIn]
    bestTrades = []
    trades = findArb(
            pairs=pairs,
            tokenIn=tokenIn,
            tokenOut=tokenOut,
            maxHops=maxHops,
            currentPairs=currentPairs,
            path=path,
            bestTrades=bestTrades,
            programStatus=programStatus,
            count=10,
            )

    logger.info(f"dfs time_use: {next(tmr)}")
    for trade in trades:
        amountsOut = trade["amountsOut"]
        # in/out
        amount_in = amountsOut[0]
        amount_out = amountsOut[-1]

        #a = getAmountsOut(web3_ins=web3_ins, amount_in=amount_in, token_address_path=[d["address"] for d in trade["path"]])
        # amount out on slide point
        amount_out_slide_point = int(amount_out*(1-slidePoint))

        # min profit
        profit_slide_point = amount_out_slide_point - amount_in

        # swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)
        # exactAmountIn, amountOutMin
        fun_args = {
                "amountIn":amount_in,
                "amountOutMin":amount_out_slide_point,
                "path":[p["address"] for p in trade["path"]],
                "to": f"'{address_tx_sender}'",
                "deadline":int(time.time()+100),
                }
        fun_with_args = "swapExactTokensForTokensSupportingFeeOnTransferTokens({amountIn}, {amountOutMin}, {path}, {to}, {deadline})".format(**fun_args)
        tx_args = {
                "from": address_tx_sender
                }
        try:
            gas = estimateGas(
                    web3_ins=web3_ins,
                    fun_with_args=fun_with_args,
                    tx_args=tx_args,
                    contract_abi=router_abi.abi(),
                    contract_address=address_router_contract)

            logger.info(f"gasUsed: {gas}")
        except:
            logger.error(f"fun estimateGas get exception:{traceback.format_exc()}")
            return

        gas_fee = gasPrice*gas

        logger.info(f"gasFee: {gas_fee/pow(10,18)} Eth")
        logger.info(f"theoryProfit: {trade['profit']/pow(10,18)} Eth")
        logger.info(f"profitSlidePoint: {profit_slide_point/pow(10,18)} Eth")
        profit_fee_on = int(profit_slide_point-gas_fee)/pow(10, startToken['decimal'])
        tag = "Insufficient"
        if profit_fee_on >= minProfit:
            tag = "Satisfy"
            logger.info(json.dumps(trade, cls=JsonCustomEncoder))
        logger.info(f"---- {tag} ProfitFeeOn ----: {profit_fee_on} Eth")

        break

if __name__ == "__main__":
    usage = "usage: python3 main.py [options] arg"
    parser = OptionParser(usage=usage,description="command descibe")
    parser.add_option("--redownload_tokens", action='store_true', dest="redownload_tokens", default=False, help="redownload tokens")
    parser.add_option("--redownload_pairs_address", action='store_true', dest="redownload_pairs_address", default=False, help="redownload pairs address")
    parser.add_option("--redownload_pairs_info", action='store_true', dest="redownload_pairs_info", default=False, help="redownload pairs info")

    (options, args) = parser.parse_args()

    white_tokens = getWhiteTokens(redownload=options.redownload_tokens)
    all_pair_info = getAllPairInfo(
            eth_http=ethereum_http,
            redownload_pairinfo=options.redownload_pairs_info,
            redownload_pairaddress=options.redownload_pairs_address,
            programStatus=programStatus,
            )

    t = Liquidity(
            eth_http=ethereum_http,
            pairs=all_pair_info,
            white_tokens=white_tokens,
            reserve_min_amount=reserveMinAmount,
            fallback_fun=main,
            )
    t.start()
    t.join()

    logger.info("---- exit ----")

