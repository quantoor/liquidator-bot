import json
from brownie import Contract
from address_dicts import addresses_lodestar
from logger import logger

def get_account_health(unitroller: Contract, ltoken: Contract, address: Address, )
    # unitroller_contract = Contract.from_explorer(addresses_lodestar['Unitroller'])
    # ltoken = Contract.from_explorer('0xCC25daC54A1a62061b596fD3Baf7D454f34c56fF')

    all_markets = unitroller.getAllMarkets() # all markets on Lodestar
    markets_in = unitroller.getAssetsIn(address) # assets for which collat is on

    total_colateral = ltoken.getAccountSnapshot(address)[1] / (10 ** ltoken.decimals()) * (ltoken.exchangeRateStored() / 10 ** 28)
    # this doesn't make too much sense, as it assumes same collateral asset as borrowed asset
    # normally would have to loop over all markets and check what asset holds most collateral in dollar terms

    borrow_balance = ltoken.borrowBalanceStored(address)

    account_liquidity = unitroller.getAccountLiquidity(address)

    print(account_liquidity) # check overall liquidity of account
    # return (error, current liquidity, shortfall)
    # liquidity is maximum account can borrow before reaching liquidation
    # if an account reaches liquidation, shortfall will return
    # USD value of abs((USD value of principal x collateral factor) - borrow balance)




# FLOW: unitroller get assets in (see where collat is active), per asset run borrow and supply
# -> collat factor * supply - borrow is account liquidity, using this, see where liquidation is imminent