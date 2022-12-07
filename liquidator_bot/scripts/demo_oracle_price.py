from brownie import *
from .util.util import get_underlying_price


def main():
    lmagic_contract = Contract('0x12997C5C005acc6933eDD5e91D9338e7635fc0BB')
    magic_contract = Contract('0x539bde0d7dbd336b79148aa742883198bbf60342')

    price = get_underlying_price(lmagic_contract, magic_contract)

    print(f'Price of {magic_contract.symbol()} is {price}')
