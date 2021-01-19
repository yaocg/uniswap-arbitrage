import json
from eth_abi import decode_abi
from web3 import Web3
from web3.contract import Contract

from abi.uniswap_router import abi as router_abi
from settings import address_router_contract

from rpc import generate_get_receipt_json_rpc
from rpc import generate_get_reserves_json_rpc
from rpc import rpc_response_batch_to_results
from rpc import generate_get_allpairs_json_rpc
from rpc import generate_get_pair_token01_json_rpc
from rpc import BatchHTTPProvider
from typing import List, Dict, Union

from abi.uniswap_pair import abi as pair_abi
from settings import ProgramStatus

def getAmountsOut(web3_ins:Web3=None, c:Contract=None, amount_in:int=None, token_address_path:List[str]=None)->List[int]:
    if not c:
        c = web3_ins.eth.contract(abi=router_abi.abi(), address=address_router_contract)
    return c.functions.getAmountsOut(amount_in,token_address_path).call(block_identifier="latest")

def get_allPairInfo(pairs_address:List[str], eth_http:str=None, batch_provider:BatchHTTPProvider=None,
        web3_ins:Web3=None, blockNumber:Union[int,str]='latest', programStatus:ProgramStatus=ProgramStatus())->List[Dict]:

    if eth_http:
        web3_ins = Web3(Web3.HTTPProvider(eth_http))
        batch_provider = BatchHTTPProvider(eth_http)

    tokens0 = []
    tokens1 = []
    for result, fun_name in [(tokens0, "token0"), (tokens1, "token1")]:
        r = list(generate_get_pair_token01_json_rpc(pairs_address, pair_abi.topic(fun_name), blockNumber))
        n = len(r)
        b = 0
        while programStatus.running():
            e = b+500
            if e > n:
                e = n
            resp = batch_provider.make_batch_request(json.dumps(r[b:e]))
            for ad in rpc_response_batch_to_results(resp):
                result.append(Web3.toChecksumAddress(ad[-40:]))
            b = e
            if b >= n:
                break

    return [{"address":pair, "token0":tokens0[i], "token1":tokens1[i]} for i,pair in enumerate(pairs_address)]

def get_allPairAddress(eth_http:str=None, batch_provider:BatchHTTPProvider=None,
        web3_ins:Web3=None, blockNumber:Union[int,str]='latest', programStatus:ProgramStatus=ProgramStatus())->List[str]:

    if eth_http:
        web3_ins = Web3(Web3.HTTPProvider(eth_http))
        batch_provider = BatchHTTPProvider(eth_http)

    r = list(generate_get_allpairs_json_rpc(web3_ins, blockNumber))
    n = len(r)
    b = 0
    results = []
    while programStatus.running():
        e = b+500
        if e > n:
            e = n
        resp = batch_provider.make_batch_request(json.dumps(r[b:e]))
        for ad in rpc_response_batch_to_results(resp):
            results.append(Web3.toChecksumAddress(ad[-40:]))
        b = e
        if b >= n:
            break

    return results

def get_reserves(web3_ins:Web3, batch_provider:BatchHTTPProvider, pairs:List[Dict], blockNumber:Union[int,str]='latest')->List[Dict]:
    r = list(generate_get_reserves_json_rpc(web3_ins, pairs, blockNumber))
    resp = batch_provider.make_batch_request(json.dumps(r))
    results = list(rpc_response_batch_to_results(resp))
    for i in range(len(results)):
        res = decode_abi(['uint256', 'uint256', 'uint256'], bytes.fromhex(results[i][2:]))
        pairs[i]['reserve0'] = res[0]
        pairs[i]['reserve1'] = res[1]
    return pairs

def get_receipts(batch_provider:BatchHTTPProvider, txhashes:List[str])->List[Dict]:
    receipts_rpc = list(generate_get_receipt_json_rpc(txhashes))
    resp = batch_provider.make_batch_request(json.dumps(receipts_rpc))
    results = rpc_response_batch_to_results(resp)
    return list(results)
