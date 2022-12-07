import json
from brownie import Contract
from .address_dicts import ltoken_addresses


def get_ltoken_contracts_dict():
    # this file contains the ABI for all lTokens
    with open('ltoken_abi.txt') as f:
        abi_str = f.read()
    abi = json.loads(abi_str)
    return {address: Contract.from_abi(name, address, abi) for name, address in ltoken_addresses.items()}


def get_underlying_price(ltoken: Contract, token: Contract) -> float:
    price_oracle_contract = Contract('0x5947189d2D7765e4f629C803581FfD06bc57dE9B')
    aggregator_address = price_oracle_contract.aggregators(ltoken.address)[0]
    return price_oracle_contract.getPriceFromChainlink(aggregator_address) / (10 ** token.decimals())
