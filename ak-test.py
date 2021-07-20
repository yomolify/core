#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'issueBooks' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY prices as parameter.
#
#
# def issueBooks(prices):
#     count = 0
#     for firstidx, firstprice in enumerate(prices):
#         print(firstidx, firstprice)
#         for secondidx, secondprice in enumerate(prices[firstidx+1:]):
#             print(secondidx, secondprice)
#             if (firstprice + secondprice) % 60 == 0:
#                 count+=1
#     return count
def secretMessage(text, hiddenMessage):
    startIdx = 0
    for hiddenCharIdx, hiddenChar in enumerate(hiddenMessage):
        print(hiddenCharIdx, hiddenChar)
        for textCharIdx, textChar in enumerate(text):
            if hiddenChar == textChar:
                # startIdx = textCharIdx+1
                print(textCharIdx, textChar)
    # if secretFound:
    #     return [startIdx, endIdx]
    # else:
    #     return 'no secret'
    return

if __name__ == '__main__':
    # print(issueBooks([10, 20, 40, 50]))
    hiddenMessage = 'sale'
    text = 'asdaklhegt'
    print(secretMessage(text, hiddenMessage))
