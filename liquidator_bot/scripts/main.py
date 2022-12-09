import requests
import json
import time
import yaml
import os
from brownie import *
from .util.logger import logger, logging
from .util.telegram_bot import TelegramBot
from .util import util
import traceback

with open('config.yaml', 'r') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

os.environ['$ARBISCAN_TOKEN'] = cfg['arbiscan_token']

# for testing
CHECK_IF_LIQUIDATABLE = True
GET_MORE_REPAY_TOKEN = True
EXECUTE_LIQUIDATION = True


class LiquidatorBot:
    def __init__(self, username: str, password: str):
        self.user = accounts.load(username, password)

        # load contract for uniswap v3 router
        self.router = interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

        # usdc is the starting balance
        self.usdc_contract = util.load_contract('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8')

        # ltoken contracts dict
        self.ltoken_contracts_dict = util.get_ltoken_contracts_dict()

        # telegram bot
        self.tg_bot = TelegramBot(cfg['telegram_chat_id'], cfg['telegram_token'])

        # unitroller
        self.unitroller = util.load_contract('0x8f2354F9464514eFDAe441314b8325E97Bf96cdc')

    def start(self):
        self.tg_bot.send('Bot started')
        logger.info('Polling liquidatable accounts...')

        while True:  # todo change this
            try:
                self._poll_liquidatable_accounts()
            except Exception as e:
                logger.error(f'Error: {e} -> {traceback.format_exc()}')
            finally:
                time.sleep(1)

    def _poll_liquidatable_accounts(self):
        res = requests.get('https://api.lodestarfinance.io/liquidatableAccounts')
        if res.status_code != 200:
            self.tg_bot.send(f'Error {res.status_code}')
            logger.error(f'Error {res.status_code}')
            time.sleep(10)
            return

        res = json.loads(res.text)

        for liquidatableAccount in res['liquidatableAccounts']:
            self._process_liquidation(liquidatableAccount)

    def _process_liquidation(self, liquidatableAccount):
        self.tg_bot.send(f'Liquidating {liquidatableAccount}')
        logger.info(f'Liquidating {liquidatableAccount}')

        borrower_address = str(liquidatableAccount['borrowAddress']).strip()
        collateral_address = str(liquidatableAccount['collateralAddress']).strip()
        repay_ltoken_address = str(liquidatableAccount['marketAddress']).strip()
        liquidatable_amount = int(liquidatableAccount['repayAmount'])

        # check if account is still liquidatable
        if CHECK_IF_LIQUIDATABLE:
            _, _, fallout = self.unitroller.getAccountLiquidity(borrower_address)
            if fallout == 0:
                logger.warning(f'Account {borrower_address} is not liquidatable')
                return

        # load contract for repay ltoken
        repay_ltoken_contract = self.ltoken_contracts_dict.get(repay_ltoken_address, None)
        if repay_ltoken_contract is None:
            logger.warning(f'Repay ltoken {repay_ltoken_address} not available in ltoken_contracts_dict')
            repay_ltoken_contract = util.load_contract(repay_ltoken_address)

        # read available balance of the repay token
        # todo to be faster, load from dict {ltoken_address: underlying_contract}
        repay_token = repay_ltoken_contract.underlying()
        repay_token_contract = util.load_contract(repay_token)
        repay_token_decimals = repay_token_contract.decimals()

        # get available balance of the repay token
        repay_token_available = self._get_balance(repay_token_contract)
        logger.debug(
            f'Balance of {repay_token_contract.symbol()} is {repay_token_available / (10 ** repay_token_decimals)}')

        # swap usdc for the repay token if needed
        if GET_MORE_REPAY_TOKEN:
            if repay_token_available < 0.9 * liquidatable_amount:
                logger.debug(
                    f'Repay token available: {repay_token_available / (10 ** repay_token_decimals)}, liquidatable amount: {liquidatable_amount / (10 ** repay_token_decimals)}')
                repay_token_amount_needed = (liquidatable_amount - repay_token_available) * 0.99  # give some margin
                repay_token_amount_needed = int(repay_token_amount_needed)

                try:
                    self._get_more_repay_token(repay_token_amount_needed, repay_ltoken_contract, repay_token_contract)
                except Exception as e:
                    logger.error(f'Could not get more of repay token: {e}')
                else:
                    # get new available balance of the repay token
                    repay_token_available = self._get_balance(repay_token_contract)
                    logger.debug(
                        f'Balance of {repay_token_contract.symbol()} is {repay_token_available / (10 ** repay_token_decimals)}')
            else:
                logger.debug(
                    f'Repay token available: {repay_token_available / (10 ** repay_token_decimals)}, no need to get more')

        # define repay amount
        repay_amount = min(repay_token_available * 0.99, liquidatable_amount * 0.99)
        repay_amount = int(repay_amount)
        logger.debug(
            f'Repay amount for token {repay_token} is {repay_amount / (10 ** repay_token_contract.decimals())}')

        # check allowance for token spend on LODESTAR Finance
        self._set_allowance(repay_token_contract, repay_ltoken_contract, repay_amount)

        # liquidate
        if EXECUTE_LIQUIDATION:
            try:
                tx = self._liquidate(repay_ltoken_contract, borrower_address, repay_amount, collateral_address)
            except Exception as e:
                # todo swap repay token back to USDC
                raise Exception(f'liquidation failed: {e}')
            else:
                logger.info(f'Liquidation executed: {tx}')

                # todo use seized lToken to get the collateral token

                # todo swap the collateral token for USDC

                # profit!

    def _liquidate(self, ltoken_contract: Contract, borrower_address: str, repay_amount: int,
                   collateral_address: str):

        logger.info('Executing liquidation...')

        tx = ltoken_contract.liquidateBorrow(
            borrower_address,
            int(repay_amount),
            collateral_address,
            {'from': self.user, 'gas_limit': 200_000, 'allow_revert': True}
        )

        # todo change this
        logger.debug(str(tx.info()))
        logger.debug(f'revert_msg: {tx.revert_msg}')
        logger.debug(f'traceback: {tx.traceback()}')
        logger.debug(f'call_trace {tx.call_trace()}')

        return tx

    def _get_balance(self, token: Contract) -> int:
        return token.balanceOf(self.user.address)

    def _get_more_repay_token(self, repay_token_needed: int, repay_ltoken_contract: Contract,
                              repay_token_contract: Contract):

        logger.debug(
            f'Swapping USDC for {repay_token_needed / 10 ** repay_token_contract.decimals()} {repay_token_contract.symbol()}')

        expected_price = util.get_underlying_price(repay_ltoken_contract, repay_token_contract)

        usdc_balance = self._get_balance(self.usdc_contract)

        # todo remove hardcoding
        max_slippage = 1  # max perc deviation from expected price
        amount_in_max = min(
            usdc_balance * 0.99,
            (repay_token_needed * expected_price) * (1 + max_slippage / 100)
        )
        amount_in_max = int(amount_in_max)

        # todo fix the logic: if not enough USDC balance, need to use exactInputSingle to maximize output

        try:
            tx = self._swap(self.usdc_contract, repay_token_contract, repay_token_needed, amount_in_max)
            logger.info(f'Executed swap {tx}')
        except Exception as e:
            raise Exception(f'swap failed: {e}')

    def _set_allowance(self, token: Contract, spender: Contract, amount: int):  # amount without decimals
        allowance = token.allowance(self.user.address, spender)
        logger.debug(
            f'Current allowance of {token.symbol()} is: {allowance / (10 ** token.decimals())}')

        # increase allowance if not enough
        if allowance < amount:
            tx = token.approve(spender, amount, {'from': self.user})
            logger.debug(
                f'Allowed {spender.address} to spend {amount / (10 ** token.decimals())} {token.symbol()}: {tx}')

    def _swap(self, token_in: Contract, token_out: Contract, amount_out: int, amount_in_max: int):
        self._set_allowance(token_in, self.router.address, amount_in_max)

        return self.router.exactOutputSingle(
            [
                token_in.address,  # token in
                token_out.address,  # token out
                3000,  # fee 0.03%
                self.user.address,  # recipient
                int(time.time() + 30) * 1000,  # deadline (UTC timestamp in ms)
                int(amount_out),  # amount out
                int(amount_in_max),  # amount in max
                0  # sqrtPriceLimitX96 - ignore this
            ],
            {'from': self.user}
        )


def main():
    logger.add_console()
    logger.add_file('.', logging.DEBUG)

    try:
        network.connect('arbitrum-main')
    except:
        pass

    bot = LiquidatorBot(username=cfg['username'], password=cfg['password'])
    bot.start()
