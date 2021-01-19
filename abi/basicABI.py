from web3 import Web3
from typing import List, Dict, Union

class BasicABI(object):
    def __init__(self, abi:List[Dict]):
        self.__abi = abi
        self.__topics = {}

        self.__calcuteTopics()

    def abi(self)->List[Dict]:
        return self.__abi

    def topic(self, fn_name:str)->Union[str, None]:
        return self.__topics.get(fn_name, None)

    def __calcuteTopics(self)->None:
        for abi in self.__abi:
            fname = abi.get("name", None)
            ftype = abi.get("type", None)
            if not fname or not ftype or ftype not in ["event", "function"]:
                continue

            inputs = abi.get("inputs", None)
            if inputs is None:
                continue

            args = ",".join(arg["internalType"] for arg in inputs)
            self.__topics.update({fname: Web3.sha3(text=f"{fname}({args})").hex()})
