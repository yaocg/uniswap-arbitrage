from decimal import Decimal
from typing import List, Dict

from common import getOptimalAmount
from common import getEaEb
from common import getAmountOut, getAmountOutByPath
from settings import ProgramStatus

def findArb(pairs:List[Dict], tokenIn:Dict, tokenOut:Dict, maxHops:int, currentPairs:List, path:List,
        bestTrades:List[Dict], programStatus:ProgramStatus=ProgramStatus(), count:int=5)->List[Dict]:

    len_path = len(path)

    for i,pair in enumerate(pairs):
        if not programStatus.running():
            return bestTrades

        if not pair:
            continue

        newPath = path.copy()
        if not pair['token0']['address'] == tokenIn['address'] and not pair['token1']['address'] == tokenIn['address']:
            continue

        if pair['reserve0']/pow(10, pair['token0']['decimal']) < 1 or pair['reserve1']/pow(10, pair['token1']['decimal']) < 1:
            continue

        if tokenIn['address'] == pair['token0']['address']:
            tempOut = pair['token1']
        else:
            tempOut = pair['token0']

        newPath.append(tempOut)
        newCurrentPairs = currentPairs + [pair]

        if tempOut['address'] == tokenOut['address'] and len_path > 2:
            Ea, Eb = getEaEb(tokenOut, newCurrentPairs)
            if Ea and Eb and Ea < Eb:
                optA = getOptimalAmount(Ea, Eb)
                if optA <= 0:
                    continue

                outA = getAmountOutByPath(tokenOut, optA, newCurrentPairs)
                profit = outA[-1] - outA[0]
                newTrade = {
                        "route": newCurrentPairs,
                        "path": newPath,
                        "amountsOut": outA,
                        "profit": profit,
                        }
                bestTrades.append(newTrade)
                bestTrades.sort(key = lambda x: x["profit"], reverse=True)
                bestTrades = bestTrades[:count]
        elif maxHops > 1 and len(pairs) > 1:
            pairs[i] = None
            bestTrades = findArb(pairs, tempOut, tokenOut, maxHops-1, newCurrentPairs, newPath, bestTrades, programStatus, count)

    return bestTrades
