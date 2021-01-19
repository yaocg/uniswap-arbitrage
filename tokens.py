import json
import traceback
from web3 import Web3
from typing import Dict

from url_request import url_get
from settings import timer
from log_builder import logger

def downloadtokens()->Dict:
    tokens_1inch = url_get("http://tokens.1inch.eth.link/")
    tokens_uniswap = url_get("https://tokens.coingecko.com/uniswap/all.json")
    tokens = {}

    for source,source_tokens in (("1inch", tokens_1inch), ("uniswap", tokens_uniswap)):
        if not source_tokens:
            continue

        try:
            tokens_aaa = json.loads(source_tokens)
            for token in tokens_aaa["tokens"]:
                if token["chainId"] != 1:
                    continue
                a = Web3.toChecksumAddress(token["address"])
                n = token["name"]
                s = token["symbol"]
                d = token["decimals"]

                tokens.update(
                        {
                            a:{
                                "name":n,
                                "symbol":s,
                                "decimals":d,
                                "source":source,
                                }
                            }
                        )
        except:
            logger.error("exec fun getWhiteTokens get exception:{traceback.format_exc()}")

    return tokens

def getWhiteTokens(tokens_file:str="files/white_tokens.json", redownload:bool=False)->Dict:
    tmr = timer()
    next(tmr)
    logger.info("Loading tokens ...")
    with open(tokens_file, "a+") as rwop:
        tokens = {}
        rwop.seek(0)
        data = rwop.read()
        if data and not redownload:
            tokens = json.loads(data)
        else:
            tokens = downloadtokens()
            rwop.truncate(0)
            rwop.write(json.dumps(tokens, indent=4))

        logger.info(f"white_tokens_num: {len(tokens)} time_use: {next(tmr)}")
        return tokens
