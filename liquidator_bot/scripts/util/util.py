import json
from brownie import Contract
from .address_dicts import ltoken_addresses


def get_ltoken_contracts_dict():
    # this file contains the ABI for all lTokens
    with open('ltoken_abi.txt') as f:
        abi_str = f.read()
    abi = json.loads(abi_str)
    return {address: Contract.from_abi(name, address, abi) for name, address in ltoken_addresses.items()}
