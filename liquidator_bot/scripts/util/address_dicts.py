addresses_lodestar = dict(
    LodestarLens="0x11caD8E4323123E12E33C88A79D97D55cd6f91aC",
    JumpRateModel_1="0x04D28F57bD9E47723F17b03e86C0d7e54De9821c",
    JumpRateModel_2="0x4640cE81be1f64D03b4731B7aC2C93A7e426Beaa",
    JumpRateModel_3="0xa23Fe46995154592974019e7A943CB4C68A98b14",
    JumpRateModel_4="0xF367462541daB82c789f113178137b10DeBf8C93",
    JumpRateModel_5="0x810c0cee2d8004dd6fc5083023724cfc923f5cdc",
    USDCDelegate="0xC46334043C053b09AD8f6E580627DBe4cf90104c",
    MAGICDelegate="0x5ab0dE7ED0fB7c83FD7C493D28edc0e393a09D7f",
    DPXDelegate="0xc8d10C89F1f6A8C3511e6bd1428b360400C11BF6",
    WBTCDelegate="0xdf10933C3dc77E2705581dD50802dC0f65e712a8",
    MIMDelegate="0x8afFABE26CA354CC7aF6A88eEE1c7547C96ecc94",
    USDTDelegate="0x6c34e36258E521F4D20cc6DE2881fB508fa5eD0B",
    plvGLPDelegate="0x4EB611232cE3a738d9eE20467A5Dd2Ecf3B2d919",
    FRAXDelegate="0x1bF86129263593396CB41d0823bAeD280822ccbA",
    lUSDC="0x5E3F2AbaECB51A182f05b4b7c0f7a5da1942De90",
    lETH="0xb4d58C1F5870eFA4B05519A72851227F05743273",
    lMAGIC="0x12997C5C005acc6933eDD5e91D9338e7635fc0BB",
    lDPX="0xc33cCF8d387DB5e84De13496E40DD83934F3251B",
    lWBTC="0xD2835B08795adfEfa0c2009B294ae84B08C6a67e",
    lMIM="0x46178d84339A04f140934EE830cDAFDAcD29Fba9",
    lDAI="0xcC3D0d211dF6157cb94b5AaCfD55D41acd3a9A7A",
    lUSDT="0xeB156f76Ef69be485c18C297DeE5c45390345187",
    lplvGLP="0xCC25daC54A1a62061b596fD3Baf7D454f34c56fF",
    lFRAX="0x5FfA22244D8273d899B6C20CEC12A88a7Cd9E460",
    Unitroller="0x8f2354F9464514eFDAe441314b8325E97Bf96cdc",  # PROXY
    Comptroller="0x50dDD0eAE0A0896f648f9E982ec65C5b8a73D02D",
    PriceOracle="0x5E3BbBDD3D191aceC0f10FB5dC5A3eb2Fcd3Ba0a",
    PriceOracleProxy="0x642f19e7641C489bf7e0e1e3039f79ce7d531058",
    Maximillion="0xBBc29a53A87e340d1986570Bafb6Bfa709081E6C",
    Reservior="0x941a4EE8a96e0EEd086D5853c3661Bc4f2357ef2",
    LODE_Token="0xF19547f9ED24aA66b03c3a552D181Ae334FBb8DB",
    TokenFix="0x8dF8E39103F196820EA56403733a79C60086608C",
    Lodestar_Chef="0x4Ce0C8C8944205C0A134ef37A772ceEE327B4c11"
)

ltoken_addresses = dict(
    lUSDC="0x5E3F2AbaECB51A182f05b4b7c0f7a5da1942De90",
    lETH="0xb4d58C1F5870eFA4B05519A72851227F05743273",
    lMAGIC="0x12997C5C005acc6933eDD5e91D9338e7635fc0BB",
    lDPX="0xc33cCF8d387DB5e84De13496E40DD83934F3251B",
    lWBTC="0xD2835B08795adfEfa0c2009B294ae84B08C6a67e",
    lMIM="0x46178d84339A04f140934EE830cDAFDAcD29Fba9",
    lDAI="0x7a668f56affd511ffc83c31666850eae9fd5bcc8",
    lUSDT="0xeB156f76Ef69be485c18C297DeE5c45390345187",
    lplvGLP="0xCC25daC54A1a62061b596fD3Baf7D454f34c56fF",
    lFRAX="0x5FfA22244D8273d899B6C20CEC12A88a7Cd9E460",
)

collateral_factors = dict(
    USDC=0.85,
    MIM=0.6,
    USDT=0.7,
    FRAX=0.75,
    DAI=0.75,
    ETH=0.8,
    BTC=0.75,
    MAGIC=0.15,
    DPX=0.15,
    plvGLP=0.8
)

reserve_factors = dict(
    USDC=0.07,
    MIM=0.25,
    USDT=0.07,
    FRAX=0.07,
    DAI=0.75,
    ETH=0.2,
    BTC=0.2,
    MAGIC=0.33,
    DPX=0.33,
    plvGLP=0.2
)

underlying_decimals = dict(
    USDC=6,
    MIM=18,
    USDT=6,
    FRAX=18,
    DAI=18,
    ETH=18,
    WBTC=8,
    MAGIC=18,
    DPX=18,
    plvGLP=18
)

CLOSE_FACTOR = 0.5  # max that can be liquidated in a single transaction. Have to wait until liquidatable againt o liquidate again
