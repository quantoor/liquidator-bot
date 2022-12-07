import requests
import json
import time
import yaml
from brownie import *
from .util.logger import logger
from .util.util import get_ltoken_contracts_dict


class LiquidatorBot:
    def __init__(self):
        # load user account using username and password
        with open('config.yaml', 'r') as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
        self.user = accounts.load(cfg['username'], cfg['password'])

        # load contract for uniswap v3 router
        self.router = interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

        # usdc is the starting balance
        self.usdc_contract = Contract.from_explorer('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8')

        # oracle contract
        self.price_oracle_contract = Contract.from_explorer("0x5947189d2D7765e4f629C803581FfD06bc57dE9B")

        # ltoken contracts dict
        self.ltoken_contracts_dict = get_ltoken_contracts_dict()

    def start(self):
        logger.info('Polling liquidatable accounts...')

        while True:  # todo change this
            try:
                self._poll_liquidatable_accounts()
            except Exception as e:
                logger.error(f'Error: {e}')
            finally:
                time.sleep(1)

    def _poll_liquidatable_accounts(self):
        res = requests.get('https://api.lodestarfinance.io/liquidatableAccounts')
        if res.status_code != 200:
            logger.error(f'Error {res.status_code}')
            return

        res = json.loads(res.text)
        logger.info(str(res))

        for liquidatableAccount in res['liquidatableAccounts']:
            self._liquidate(liquidatableAccount)

    def _liquidate(self, liquidatableAccount):
        logger.info(f'Liquidating {liquidatableAccount}...')

        borrower_address = liquidatableAccount['borrowAddress']
        collateral_address = liquidatableAccount['collateralAddress']
        repay_ltoken_address = liquidatableAccount['marketAddress']
        liquidatable_amount = liquidatableAccount['repayAmount']

        # load contract for repay ltoken
        repay_ltoken_contract = self.ltoken_contracts_dict.get(repay_ltoken_address, None)
        if repay_ltoken_contract is None:
            logger.warning(f'Repay ltoken {repay_ltoken_address} not available in ltoken_contracts_dict')
            try:
                repay_ltoken_contract = Contract.from_explorer(repay_ltoken_address)
            except Exception as e:
                raise Exception(f'could not load contract for market_address {repay_ltoken_address}: {e}')

        # read available balance of the repay token
        # todo to be faster, load from dict {ltoken_address: underlying_contract}
        repay_token = repay_ltoken_contract.underlying()
        repay_token_contract = Contract.from_explorer(repay_token)
        repay_token_decimals = repay_token_contract.decimals()

        # get available balance of the repay token
        repay_token_available = self._get_balance(repay_token_contract)
        logger.debug(
            f'Balance of {repay_token_contract.symbol()} is {repay_token_available / (10 ** repay_token_decimals)}')

        # swap usdc for the repay token if needed
        if repay_token_available < 0.9 * liquidatable_amount:
            logger.debug(
                f'Repay token available: {repay_token_available / (10 ** repay_token_decimals)}, liquidatable amount: {liquidatable_amount / (10 ** repay_token_decimals)}')
            repay_token_needed = liquidatable_amount - repay_token_available * 1.01  # give some margin
            repay_token_needed_norm = repay_token_needed / 10 ** repay_token_decimals

            self._get_more_repay_token(repay_token_needed_norm, repay_ltoken_contract, repay_token_contract)

            # get new available balance of the repay token
            repay_token_available = self._get_balance(repay_token_contract)
            logger.debug(
                f'Balance of {repay_token_contract.symbol()} is {repay_token_available / (10 ** repay_token_decimals)}')

        # define repay amount
        repay_amount = min(repay_token_available * 0.99, liquidatable_amount * 0.99)
        logger.debug(f'Repay amount for token {repay_token} is {repay_amount}')

        # check allowance for token spend on LODESTAR Finance
        self._set_allowance(repay_token_contract, repay_ltoken_contract, repay_amount / (10 ** repay_token_decimals))

        # liquidate
        logger.info('Executing liquidation...')
        try:
            tx = repay_ltoken_contract.liquidateBorrow(
                borrower_address,
                int(repay_amount),
                collateral_address,
                {'from': self.user}
            )
        except Exception as e:
            raise Exception(f'liquidation failed: {e}')

        logger.info(f'Liquidation executed: {tx}')

        # todo use seized lToken to get the collateral token

        # todo swap the collateral token to usdc

        # profit!

    def _get_balance(self, token: Contract) -> int:
        return token.balanceOf(self.user.address)

    def _get_more_repay_token(self, repay_token_needed_norm: int, repay_ltoken_contract: Contract,
                              repay_token_contract: Contract):

        logger.info(f'Swapping USDC for {repay_token_needed_norm} {repay_token_contract.symbol()}')

        expected_price = self._get_underlying_price(repay_ltoken_contract, repay_token_contract)

        usdc_balance = self._get_balance(self.usdc_contract) / (10 ** self.usdc_contract.decimals())

        # todo remove hardcoding
        max_slippage = 1  # max perc deviation from expected price
        amount_in_max = min(usdc_balance * 0.99, (repay_token_needed_norm * expected_price) * (1 + max_slippage / 100))

        # todo fix the logic: if not enough USDC balance, need to use exactInputSingle to maximize output

        try:
            tx = self._swap(self.usdc_contract, repay_token_contract, repay_token_needed_norm, amount_in_max)
            logger.info(f'Executed swap {tx}')
        except Exception as e:
            raise Exception(f'swap failed: {e}')

    def _set_allowance(self, token_spend: Contract, token_allowed: Contract, amount: int): # amount without decimals
        allowance = token_spend.allowance(self.user.address, token_allowed)
        print(f'Current allowance of {token_spend.symbol()} is: {allowance / (10 ** token_spend.decimals())}')

        # increase allowance if not enough
        if allowance < (amount * 10 ** token_spend.decimals()):
            tx = token_spend.approve(token_allowed, int(amount * 10 ** token_spend.decimals()), {'from': self.user})
            print(f'Allowed router to spend {amount} {token_spend.symbol()}: {tx}')


    def _swap(self, token_in: Contract, token_out: Contract, amount_out: int, amount_in_max: int):
        self._set_allowance(token_in, self.router.address, amount_in_max ** token_in.decimals())

        return self.router.exactOutputSingle(
            [
                token_in.address,  # token in
                token_out.address,  # token out
                3000,  # fee 0.03%
                self.user.address,  # recipient
                int(time.time() + 30) * 1000,  # deadline (UTC timestamp in ms)
                int(amount_out * 10 ** token_out.decimals()),  # amount out
                int(amount_in_max * 10 ** token_in.decimals()),  # amount in max
                0  # sqrtPriceLimitX96 - ignore this
            ],
            {'from': self.user}
        )

    def _get_underlying_price(self, ltoken: Contract, token: Contract) -> float:
        aggregator_address = self.price_oracle_contract.aggregators(ltoken.address)[0]
        return self.price_oracle_contract.getPriceFromChainlink(aggregator_address) / (10 ** token.decimals())


def main():
    logger.add_console()
    logger.info('Connecting to network...')

    try:
        network.connect('arbitrum-main')
    except:
        pass

    bot = LiquidatorBot()
    bot.start()
