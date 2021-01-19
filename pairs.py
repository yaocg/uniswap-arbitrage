import json
import traceback
from web3 import Web3
from typing import List
from typing import Dict

from settings import timer
from settings import ProgramStatus
from events import get_allPairAddress
from events import get_allPairInfo
from log_builder import logger

def getAllPairAddress(eth_http:str, pairs_file:str="files/all_pair_address.json",
        redownload:bool=False, programStatus:ProgramStatus=ProgramStatus()) -> List[str]:

    tmr = timer()
    next(tmr)
    logger.info("Loading all pair address ...")
    with open(pairs_file, "a+") as rwop:
        all_pairs_address = []
        rwop.seek(0)
        data = rwop.read()
        if data and not redownload:
            all_pairs_address = json.loads(data)
        else:
            all_pairs_address = get_allPairAddress(eth_http=eth_http, programStatus=programStatus)
            rwop.truncate(0)
            rwop.write(json.dumps(all_pairs_address, indent=4))

        logger.info(f"pairs_address_num: {len(all_pairs_address)} time_use: {next(tmr)}")
        return all_pairs_address


def getAllPairInfo(eth_http:str, pairs_file:str="files/all_pair_info.json",
        redownload_pairinfo:bool=False, redownload_pairaddress:bool=False, programStatus:ProgramStatus=ProgramStatus()) -> List[Dict]:

    tmr = timer()
    next(tmr)
    logger.info("Loading all pair info...")
    with open(pairs_file, "a+") as rwop:
        all_pair_info = []
        rwop.seek(0)
        data = rwop.read()
        if data and not redownload_pairinfo:
            all_pair_info = json.loads(data)
        else:
            all_pair_address = getAllPairAddress(eth_http=eth_http, redownload=redownload_pairaddress, programStatus=programStatus)
            all_pair_info = get_allPairInfo(eth_http=eth_http, pairs_address=all_pair_address, programStatus=programStatus)
            rwop.truncate(0)
            rwop.write(json.dumps(all_pair_info, indent=4))

        logger.info(f"pairs_info_num: {len(all_pair_info)} time_use: {next(tmr)}")
        return all_pair_info

