from brownie import *
import os
import yaml

with open('config.yaml', 'r') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# set arbitrum scan api token
os.environ['$ARBISCAN_TOKEN'] = cfg['arbiscan_token']

try:
    network.connect('arbitrum-goerli')
except:
    pass

# load user account using username and password
user = accounts.load(cfg['username'], cfg['password'])

borrower_address = '0x319f4fb1AF38733824439b996Df33673Fd1485dF'

usdc = Contract('0x21Dbd0C4f580e636aBc68327669A15239C82eee0')
print(usdc.address)

# goerli
# unitroller_address = '0xeB156f76Ef69be485c18C297DeE5c45390345187'
# comptroller_address = '0x5e7D76fa33699d2fa87a43e0ea88D03154602De4'
# unitroller = Contract.from_explorer(unitroller_address, as_proxy_for=comptroller_address)

# mainnet
# unitroller_address = '0x8f2354F9464514eFDAe441314b8325E97Bf96cdc'
# comptroller_address = '0x50dDD0eAE0A0896f648f9E982ec65C5b8a73D02D'
# unitroller = Contract.from_explorer(unitroller_address, as_proxy_for=comptroller_address)


def main():
    # res = unitroller.getAccountLiquidity(borrower_address)
    # print(res)
    pass
