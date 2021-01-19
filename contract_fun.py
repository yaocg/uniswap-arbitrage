from web3 import Web3
from typing import List, Dict

from log_builder import logger

def estimateGas(web3_ins:Web3, fun_with_args:str, tx_args:Dict, contract_abi:List[Dict], contract_address:str)->int:
    c = web3_ins.eth.contract(abi=contract_abi, address=contract_address)
    f = f"c.functions.{fun_with_args}.estimateGas({tx_args})"
    try:
        return eval(f)
    except:
        raise
    finally:
        logger.info("estimategas_contract_fun:{}".format(f))

