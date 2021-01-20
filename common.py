from decimal import Decimal
from typing import List, Dict, Union

import json
d997 = Decimal(997)
d1000 = Decimal(1000)

def getOptimalAmount(Ea, Eb):
    if Ea > Eb:
        return None
    return int((Decimal.sqrt(Ea*Eb*d997*d1000)-Ea*d1000)/d997)

def getEaEb(tokenIn:Dict, pairs:List[Dict])->(int,int):
    Ea = None
    Eb = None
    tokenOut = None
    pairs_len = len(pairs)

    if pairs_len < 2:
        return Ea, Eb

    Ea = pairs[0]["reserve0"]
    Eb = pairs[0]["reserve1"]
    if tokenIn['address'] == pairs[0]['token1']['address']:
        Ea,Eb = Eb,Ea
        tokenOut = pairs[0]['token1']
    else:
        tokenOut = pairs[0]['token0']

    for idx in range(1, pairs_len):
        pair = pairs[idx]
        Rb1 = pair['reserve0']
        Rc =  pair['reserve1']
        if tokenOut['address'] == pair['token1']['address']:
            Rb1,Rc = Rc,Rb1
            tokenOut = pair['token0']
        else:
            tokenOut = pair['token1']

        Ea = int(d1000*Ea*Rb1/(d1000*Rb1+d997*Eb))
        Eb = int(d997*Eb*Rc/(d1000*Rb1+d997*Eb))
    return Ea, Eb

def getAmountOutByPath(tokenIn:Dict, amountIn:int, pairs:List[Dict])->(bool, int):
    amountOut = [amountIn] + [None for _ in pairs]
    tokenOut = tokenIn
    status = False
    for i,pair in enumerate(pairs):
        if pair['token0']['address'] == tokenOut['address']:
            tokenOut = pair['token1']
            status, amountOut[i+1] = getAmountOut(amountOut[i], pair['reserve0'], pair['reserve1'])
        elif pair['token1']['address'] == tokenOut['address']:
            tokenOut = pair['token0']
            status, amountOut[i+1] = getAmountOut(amountOut[i], pair['reserve1'], pair['reserve0'])
        if not status:
            break
    return status, amountOut

def getAmountOut(amountIn:int, reserveIn:int, reserveOut:int)->(bool, int):
    if amountIn <= 0 or reserveIn <=0 or reserveOut <=0:
        return False, 0

    return True, int(d997*amountIn*reserveOut/(d1000*reserveIn+d997*amountIn))
