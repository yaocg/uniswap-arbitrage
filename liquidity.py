import time
import json
import threading
import traceback
from web3 import Web3
from web3.datastructures import AttributeDict
from typing import List, Dict, Callable

from events import get_reserves
from rpc import BatchHTTPProvider

from settings import programStatus
from settings import timer
from abi.uniswap_pair import abi as pair_abi

from log_builder import logger

class Liquidity(threading.Thread):
    def __init__(self, eth_http:str, pairs:List[Dict], white_tokens:Dict, reserve_min_amount:int, fallback_fun:Callable[[List[Dict]], None]):
        threading.Thread.__init__(self)

        self.__lock = threading.Lock()
        self.__eth_http = eth_http
        self.__all_pairs = pairs
        self.__white_tokens = white_tokens
        self.__reserve_min_amount = reserve_min_amount
        self.__fallback_fun = fallback_fun
        self.__timer = timer()

        self.__white_pairs_change = True

        next(self.__timer)
        self.__white_pairs_index, self.__white_pairs_list = Liquidity.__filterPairs(self.__all_pairs, self.__white_tokens)
        logger.info(f"Liquidity white_pairs_num: {len(self.__white_pairs_list)} time_use: {next(self.__timer)}")

    def __filterPairs(pairs:List[Dict], white_tokens:Dict)->(Dict, List[Dict]):
        white_pairs_index = {}
        white_pairs_list = []

        for pair in pairs:
            t0_check = pair["token0"]
            t1_check = pair["token1"]
            t0 = white_tokens.get(t0_check, None)
            t1 = white_tokens.get(t1_check, None)

            if not t0 or not t1:
                continue

            ca = pair["address"]
            index = white_pairs_index.get(ca, -1)
            value = {
                    "enable": True,
                    "address": ca,
                    "reserve0": None,
                    "reserve1": None,
                    "block":None,
                    "token0": {
                        "address": t0_check,
                        "symbol": t0["symbol"],
                        "decimal": t0["decimals"],
                        },
                    "token1": {
                        "address": t1_check,
                        "symbol": t1["symbol"],
                        "decimal": t1["decimals"]
                        }
                    }
            if index == -1:
                white_pairs_list.append(value)
                white_pairs_index.update({ca: len(white_pairs_list)-1})
            else:
                white_pairs_list[index] = value

        return white_pairs_index, white_pairs_list

    def __dealEvent(self, event:AttributeDict, blkEventsCount:Dict)->int:
        self.__white_pairs_change = True
        index = self.__white_pairs_index.get(event.address, None)
        if not index:
            return 0

        pair = self.__white_pairs_list[index]
        pair["reserve0"] = event.args.reserve0
        pair["reserve1"] = event.args.reserve1
        pair["block"] = event.blockNumber
        blkEventsCount.update(
                {
                    event.blockNumber: 1+blkEventsCount.setdefault(event.blockNumber, 0)
                    }
                )

        self.__disablePair(index)
        return 1

    def __disablePair(self, index:int):
        pair = self.__white_pairs_list[index]
        t0 = pair["reserve0"]/pow(10, pair["token0"]["decimal"])<self.__reserve_min_amount
        t1 = pair["reserve1"]/pow(10, pair["token1"]["decimal"])<self.__reserve_min_amount
        if t0 or t1:
            pair.update({"enable":False})
            return 1
        return 0

    def __updateReserves(self, web3_ins:Web3, batch_provider_ins:BatchHTTPProvider)->None:
        next(self.__timer)
        get_reserves(web3_ins, batch_provider_ins, self.__white_pairs_list)
        pairs_len = len(self.__white_pairs_list)
        num = 0
        for i in range(0, pairs_len):
            num+=self.__disablePair(i)

        self.__saveToFile()
        logger.info(f"__updateReserves all_pair_num: {pairs_len}")
        logger.info(f"__updateReserves disable_pair_num: {num}")
        logger.info(f"__updateReserves enable_pair_num: {pairs_len-num}")
        logger.info(f"__updateReserves time_use: {next(self.__timer)}")

    def __saveToFile(self, file_path:str="files/latest_reserves.json")->None:
        if not self.__white_pairs_change:
            return
        self.__white_pairs_change = False
        with open(file_path, "w") as wop:
            wop.write(json.dumps(self.__white_pairs_list, indent=4))

    def run(self):
        sync_topic = pair_abi.topic("Sync")
        while programStatus.running():
            try:
                web3_ins = Web3(Web3.HTTPProvider(self.__eth_http))
                batch_provider = BatchHTTPProvider(self.__eth_http)

                # update event from latest block
                latest_block = web3_ins.eth.getBlock("latest")
                logger.info(f"latest_block: {latest_block.number}")

                with self.__lock:
                    self.__updateReserves(web3_ins, batch_provider)

                attached_pair_contract = web3_ins.eth.contract(abi=pair_abi.abi())
                event_filter = attached_pair_contract.events.Sync().createFilter(fromBlock=latest_block.number, toBlock="latest", topics=[sync_topic])
                block_filter = web3_ins.eth.filter("latest")

                # all events for latest block
                events = event_filter.get_all_entries()
                if events:
                    with self.__lock:
                        blk_events_count = {}
                        for event in events:
                            self.__dealEvent(event, blk_events_count)
                        logger.info(f"Block liquidity_update_num(keys:{len(blk_events_count.keys())}): {json.dumps(blk_events_count)}")

                while programStatus.running():
                    blocks = block_filter.get_new_entries()
                    events = event_filter.get_new_entries()
                    if events:
                        with self.__lock:
                            blk_events_count = {}
                            for event in events:
                                self.__dealEvent(event, blk_events_count)
                            logger.info(f"Block liquidity_update_num(keys:{len(blk_events_count.keys())}): {json.dumps(blk_events_count)}")

                    if not blocks:
                        self.__saveToFile()
                        continue

                    logger.info(f"new blocks: {[b.hex() for b in blocks]}")

                    with self.__lock:
                        # deepcopy self.__white_pairs_list
                        x = []
                        for d in self.__white_pairs_list:
                            if not d["enable"]:
                                continue

                            x1 = {}
                            for k,v in d.items():
                                v1 = v
                                if type(v) == dict:
                                    v1 = {tk:tv for tk,tv in v.items()}
                                x1.update({k:v1})
                            x.append(x1)

                        try:
                            self.__fallback_fun(x)
                        except:
                            logger.error(f"exec __fallback_fun(x) get exception:{traceback.format_exc()}")
            except:
                logger.error(f"exec Liquidity get exception:{traceback.format_exc()}")
                logger.warning("reconnect ...")
                time.sleep(3)
