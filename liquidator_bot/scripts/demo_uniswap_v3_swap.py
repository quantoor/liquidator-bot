from brownie import *
import time
import os
import yaml

with open('config.yaml', 'r') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# set arbitrum scan api token
os.environ['$ARBISCAN_TOKEN'] = cfg['arbiscan_token']

try:
    network.connect('arbitrum-main')
except:
    pass

# load user account using username and password
user = accounts.load(cfg['username'], cfg['password'])

# load contract for uniswap v3 router
router = interface.ISwapRouter('0xE592427A0AEce92De3Edee1F18E0157C05861564')

# load contracts for tokens to swap
usdc = Contract('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8')
weth = Contract('0x82af49447d8a07e3bd95bd0d56f35241523fbab1')

# define decimals
usdc_dec = 10 ** usdc.decimals()
weth_dec = 10 ** weth.decimals()


def main():
    # swap WETH for USDC

    # define input
    weth_price = 1250  # $ price of WETH
    amount_usdc_out = 1  # 1 USDC out
    amount_weth_in_max = (amount_usdc_out / weth_price) * 1.01  # allow max 1% 'slippage'
    timeout = 30  # max seconds to execute tx

    print(f'Available WETH balance: {weth.balanceOf(user.address) / weth_dec}')

    allowance = weth.allowance(user.address, router.address)
    print(f'Current allowance of WETH is: {allowance / weth_dec}')

    # increase allowance if not enough
    if allowance < amount_weth_in_max * weth_dec:
        tx = weth.approve(router.address, amount_weth_in_max * weth_dec, {'from': user})
        print(f'Allowed router to spend {amount_weth_in_max} WETH: {tx}')

    # execute swap
    print('Executing swap...')
    tx = router.exactOutputSingle(
        [
            weth.address,  # token in
            usdc.address,  # token out
            3000,  # fee 0.03%
            user.address,  # recipient
            int(time.time() + timeout) * 1000,  # deadline (UTC timestamp in ms)
            int(amount_usdc_out * usdc_dec),  # amount out
            int(amount_weth_in_max * weth_dec),  # amount in max
            0  # sqrtPriceLimitX96 - ignore this
        ],
        {'from': user}
    )

    print(f'Swap done: {tx}')
