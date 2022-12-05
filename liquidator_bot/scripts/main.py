import requests
import json
import time
from logger import logger
from brownie import *
import yaml

logger.add_console()
logger.info('Connecting to network...')

try:
    network.connect('arbitrum-main')
except:
    pass

# load user account using username and password
with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
user = accounts.load(config['username'], config['password'])

# load contract for uniswap v3 router
router = interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

# usdc is the starting balance
usdc_contract = Contract.from_explorer('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8')


def poll_liquidatable_accounts():
    res = requests.get('https://api.lodestarfinance.io/liquidatableAccounts')
    if res.status_code != 200:
        logger.error(f'Error {res.status_code}')
        return

    res = json.loads(res.text)
    logger.info(str(res))

    for liquidatableAccount in res['liquidatableAccounts']:
        liquidate(liquidatableAccount)


def liquidate(liquidatableAccount):
    logger.info(f'Liquidating {liquidatableAccount}...')

    borrower_address = liquidatableAccount['borrowAddress']
    collateral_address = liquidatableAccount['collateralAddress']
    repay_token = liquidatableAccount['marketAddress']
    liquidatable_amount = liquidatableAccount['repayAmount']

    try:
        repay_token_contract = Contract.from_explorer(repay_token)
        # todo handle unverified contracts
    except Exception as e:
        raise Exception(f'could not load contract for market_address {repay_token}: {e}')

    # read available balance of the repay token
    repay_token_available = get_balance(repay_token_contract)
    logger.info(f'Available balance for token {repay_token_contract.symbol()} is {repay_token_available}')

    # swap usdc for the repay token if needed
    if repay_token_available < 0.9 * liquidatable_amount:
        logger.info(f'Repay token available: {repay_token_available}, liquidatable amount: {liquidatable_amount}')
        repay_token_needed = liquidatable_amount - repay_token_available * 1.01  # give some margin

        # todo get $ price of repay token from oracle/coingecko/CEX
        expected_price = 1

        logger.info(f'Swapping USDC for {repay_token_needed} {repay_token_contract.symbol()}')

        repay_token_needed_norm = repay_token_needed / 10 ** repay_token.decimals()
        amount_in_max = (repay_token_needed_norm / expected_price) * 1.01  # max deviation from expected price

        # todo logic: if balance not enough, exactInputSingle must be used
        # available USDC balance
        # usdc_balance = get_balance(usdc_contract)

        try:
            tx = swap(usdc_contract, repay_token_contract, repay_token_needed, amount_in_max)
            logger.info(f'Executed swap {tx}')
        except Exception as e:
            raise Exception(f'swap failed: {e}')

    # read again available balance of the repay token
    repay_token_available = get_balance(repay_token_contract)
    logger.info(f'Available balance for token {repay_token_contract.symbol()} is {repay_token_available}')

    # define repay amount
    repay_amount = min(repay_token_available, liquidatable_amount * 0.99)
    logger.info(f'Repay amount for token {repay_token} is {requests}')

    # liquidate
    logger.info('Executing liquidation...')
    try:
        tx = repay_token_contract.liquidateBorrow(borrower_address, repay_amount, collateral_address, {'from': user})
    except Exception as e:
        raise Exception(f'liquidation failed: {e}')

    logger.info(f'Liquidation executed: {tx}')

    # todo use seized lToken to get the collateral token

    # todo swap the collateral token to usdc

    # profit!


def get_balance(token: Contract) -> int:
    return token.balanceOf(user.address)


def swap(token_in: Contract, token_out: Contract, amount_out: int, amount_in_max: int):
    return router.exactOutputSingle(
        [
            token_in.address,  # token in
            token_out.address,  # token out
            3000,  # fee 0.03%
            user.address,  # recipient
            int(time.time() + 30) * 1000,  # deadline (UTC timestamp in ms)
            int(amount_out * 10 ** token_out.decimals()),  # amount out
            int(amount_in_max * 10 ** token_in.decimals()),  # amount in max
            0  # sqrtPriceLimitX96 - ignore this
        ],
        {'from': user}
    )


def main():
    logger.info('Listening to liquidatable accounts...')
    while True:
        try:
            poll_liquidatable_accounts()
        except Exception as e:
            logger.error(f'Error: {e}')
        finally:
            time.sleep(1)


if __name__ == '__main__':
    main()
