import requests
import json
import time
from util.logger import logger
from brownie import *


def listen():
    res = requests.get('https://api.lodestarfinance.io/liquidatableAccounts')
    if res.status_code != 200:
        logger.error(f'Error {res.status_code}')
        return

    res = json.loads(res.text)
    logger.info(str(res))

    for liquidatableAccount in res['liquidatableAccounts']:
        liquidate(liquidatableAccount)


def liquidate(liquidatableAccount):
    logger.info(f'Liquidating {liquidatableAccount}')

    # liquidation code here
    # borrower_address = liquidatableAccount['borrowAddress']
    # collateral_address = liquidatableAccount['collateralAddress']
    # market_address = liquidatableAccount['marketAddress']
    # liquidatable_amount = liquidatableAccount['repayAmount']


def main():
    logger.add_console()
    logger.info('Connecting to network...')

    try:
        network.connect('arbitrum-main')
    except:
        pass

    logger.info('Listening to liquidatable accounts...')
    while True:
        try:
            listen()
        except Exception as e:
            logger.error(str(e))
        finally:
            time.sleep(10)


if __name__ == '__main__':
    main()
