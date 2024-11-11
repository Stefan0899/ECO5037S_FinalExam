#Libraries required
from algosdk import account, transaction
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, AssetTransferTxn, ApplicationNoOpTxn
import json, time
###############

#Initizalize Algorand Client
algod_address = "https://testnet-api.4160.nodely.dev"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

#####################

# #Generate and print new accounts
# def generate_account():
#     private_key, address = account.generate_account()
#     print(f"Address: {address}")
#     print(f"Private Key: {private_key}")
#     return private_key, address

# private_key, address = generate_account()

accounts = {
    "liquidity_provider1": {
        "address": "MK34OBXDLW2VF5LB77FDL2OZE3WECY3WM35VQ5RDNNZJUEDENZD63EFGTA",
        "private_key": "gC3pEdqqVHYBdqtNtIEFWDXa/a2RmOH15O0oAXFikABit8cG4121UvVh/8o16dkm7EFjdmb7WHYja3KaEGRuRw=="
    },
    "liquidity_provider2": {
        "address": "4WHCTSHPXYO55OQ57QROJMJLDFURRCRUW6U4PPSWREYWSBBPF3W4EHW6XU",
        "private_key": "Pgw3SD+RjaB3Sul5DMOp73nyP0HLAW2wqvZjt3INWG3ljinI774d3rod/CLksSsZaRiKNLepx75WiTFpBC8u7Q=="
    },
    "liquidity_pool": {
        "address": "LAT7ARXCRPPM3DGAU7CMRFIKOC2SPD6SYHUQR7LSHO5QG75PVN62UFJ654",
        "private_key": "rZpskRuo/JxAD8IPD8Tf/YneMTuC4SNlYnH3MSEqcBtYJ/BG4ovezYzAp8TIlQpwtSeP0sHpCP1yO7sDf6+rfQ=="
    },
    "creator": {
        "address": "3MJRJ2LVA7ASC5YF4LBO444Z5JCVR4U5BKL25IBZLQY55A4YLSDTG6YIYU",
        "private_key": "GGSjA5XbKiYVmI66gOk4BQYmfs9hQKoIJ7IRg7ccGeHbExTpdQfBIXcF4sLuc5nqRVjynQqXrqA5XDHeg5hchw=="
    },
    "trader1": {
        "address": "4BFC7EPHEWOCAX2MFMWRZUULQ4VEF4XWL5RSGOZVN76DQ2S7UWPAZC3BPA",
        "private_key": "Xuxvx4vhNJAwS30BiexJZ6pvy8CiJMofPUhWkABzLZHgSi+R5yWcIF9MKy0c0ouHKkLy9l9jIzs1b/w4al+lng=="
    },
    "trader2": {
        "address": "T6OTGYPTX7T2GJPQ3CY2E2WGTGQAJF7VQYWI2IIHX7OKNIUTJ53Q4VQGXE",
        "private_key": "+ABtsQiTZ1Vdsnhl6hen2WWyL9KPBampwFzbReMZ9KSfnTNh87/noyXw2LGiasaZoASX9YYsjSEHv9ymopNPdw=="
    },
}


def check_balance(algod_client, address, asset_id, asset_name="ALGO"):
    """
    Check the balance of the specified asset for a given account.
    If asset_name is "ALGO", it returns the ALGO balance.
    Otherwise, it checks for the specified asset ID balance (e.g., UCTZAR).
    """
    account_info = algod_client.account_info(address)
    
    # Check ALGO balance
    if asset_name == "ALGO":
        algo_balance = account_info['amount'] / 1_000_000  # Convert from microAlgos to ALGOs
        return algo_balance

    # Check specified asset balance (e.g., UCTZAR)
    for asset in account_info.get('assets', []):
        if asset['asset-id'] == asset_id:
            return asset['amount'] / 100  # Assuming 2 decimal places for assets like UCTZAR

    # If asset not found, return 0 balance
    return 0

##########################

#Mint UCTZAR Stablecoin

def create_uctzar_asset(algod_client, creator_address, creator_private_key):
    # Fetch recommended parameters for the network
    params = algod_client.suggested_params()
    
    # Define asset parameters
    total_supply = 10_000     # Total supply of UCTZAR set to 100
    decimals = 2              # Decimal places (e.g., 100 represents 1.00 UCTZAR)
    unit_name = "UCTZAR"       # Short name for the asset
    asset_name = "South African Rand Stablecoin"

    # Create the asset creation transaction
    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=total_supply,
        decimals=decimals,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address
    )

    # Sign the transaction with the creator's private key
    signed_txn = txn.sign(creator_private_key)

    # Send the transaction to the Algorand network
    txid = algod_client.send_transaction(signed_txn)

    # Wait for confirmation and get the asset ID
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
        asset_id = confirmed_txn['asset-index']
        print(f"UCTZAR asset created with Asset ID: {asset_id}")
        return asset_id
    except Exception as e:
        print(f"Asset creation failed: {e}")
        return None
    

##################

# Opt-in function for UCTZAR asset

def opt_in_to_asset(algod_client, account_address, account_private_key, asset_id):
    params = algod_client.suggested_params()
    txn = AssetTransferTxn(
        sender=account_address,
        sp=params,
        receiver=account_address,  # Opt-in to receive the asset
        amt=0,                      # Amount 0 for opt-in
        index=asset_id              # Asset ID for UCTZAR
    )
    signed_txn = txn.sign(account_private_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Opt-in Transaction ID for {account_address}: {txid}")
    transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"{account_address} successfully opted in to asset ID {asset_id}")

# ###############

#Transfer UCTZAR from Creator to liquidity providers.

def transfer_asset(algod_client, sender_address, sender_private_key, receiver_address, amount, asset_id):
    params = algod_client.suggested_params()
    txn = AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount,
        index=asset_id
    )
    signed_txn = txn.sign(sender_private_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transfer Transaction ID: {txid}")
    transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Transferred {amount / 100:.2f} UCTZAR to {receiver_address}")

############

#Create LP tokens for liquidity providers

def create_lp_token(algod_client, creator_address, creator_private_key, total_supply=1_000_000):
    """
    Create a liquidity pool (LP) token to represent shares in the pool.
    """
    params = algod_client.suggested_params()
    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=total_supply,     # Total supply of LP tokens
        decimals=0,              # No decimals for simplicity
        default_frozen=False,
        unit_name="LP-TOKEN",
        asset_name="Liquidity Pool Token",
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address
    )

    signed_txn = txn.sign(creator_private_key)
    txid = algod_client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(algod_client, txid, 4)

    # Get the LP token ID
    asset_id = algod_client.pending_transaction_info(txid)['asset-index']
    print(f"LP Token created with Asset ID: {asset_id}")
    return asset_id

####################

def add_liquidity(algod_client, provider_address, provider_private_key, algo_amount, uctzar_amount, asset_id, lp_asset_id, lp_total_supply):
    params = algod_client.suggested_params()

    # Transfer ALGOs to the Liquidity Pool account
    algo_txn = transaction.PaymentTxn(
        sender=provider_address,
        receiver=accounts["liquidity_pool"]["address"],
        amt=int(algo_amount * 1_000_000),  # Convert ALGO amount to microAlgos
        sp=params
    )
    print("Algo amount added to pool:", algo_amount)
    # Transfer UCTZAR to the Liquidity Pool account
    uctzar_txn = AssetTransferTxn(
        sender=provider_address,
        receiver=accounts["liquidity_pool"]["address"],
        amt=int(uctzar_amount),
        index=asset_id,
        sp=params
    )

    print("UCTZAR amount added to pool:", uctzar_amount)
    # Calculate LP tokens to issue based on provider's share of the pool
    lp_tokens_issued = lp_total_supply - check_balance(algod_client, accounts["liquidity_pool"]["address"], lp_asset_id, "LP-TOKEN")*100
    print("LP Tokens Issued", lp_tokens_issued)
    # Calculate provider's contribution value
    provider_value = algo_amount * 2 + uctzar_amount/100
    print("Provider Value", provider_value)
    #Check if tokens are available
        # Avoid division by zero: if the pool has no liquidity, set provider share to 1 (first provider)
    if lp_total_supply <= lp_tokens_issued + provider_value:
        print("Liquidity pool maximum reached")
    else:
        lp_tokens_to_issue = int(provider_value)
        print("LP tokens to issue:", lp_tokens_to_issue)
    
    # Issue LP tokens to provider
    lp_token_txn = AssetTransferTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=provider_address,
        amt=lp_tokens_to_issue,
        index=lp_asset_id,
        sp=params
    )
    # Group and sign the transactions
    gid = transaction.calculate_group_id([algo_txn, uctzar_txn, lp_token_txn])
    algo_txn.group = gid
    uctzar_txn.group = gid
    lp_token_txn.group = gid


    signed_algo_txn = algo_txn.sign(provider_private_key)
    signed_uctzar_txn = uctzar_txn.sign(provider_private_key)
    signed_lp_token_txn = lp_token_txn.sign(accounts["liquidity_pool"]["private_key"])

    # Send grouped transactions
    txid = algod_client.send_transactions([signed_algo_txn, signed_uctzar_txn, signed_lp_token_txn])
    transaction.wait_for_confirmation(algod_client, txid, 4)
    print(f"Liquidity added to pool from {provider_address}. Transaction ID: {txid}")


#######################

# Trade algos for UCTZAR

def execute_trade_algo_for_uctzar(algod_client, trader_address, trader_private_key, algo_amount, asset_id, fee_percent=0.3):
    """
    Execute a trade where the trader exchanges ALGOs for UCTZAR from the liquidity pool.
    The fee is distributed proportionally to both liquidity providers.
    """
    params = algod_client.suggested_params()
    
    pool_algo_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], None, "ALGO")-10
    pool_uctzar_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], uctzar_asset_id, "UCTZAR")

    # Calculate the constant product k
    k = pool_algo_balance * pool_uctzar_balance
    
    # Calculate new balances after ALGO deposit
    new_algo_balance = pool_algo_balance + algo_amount
    new_uctzar_balance = k / new_algo_balance
    uctzar_out = pool_uctzar_balance - new_uctzar_balance
    
    # Deduct the trading fee
    fee = uctzar_out * fee_percent
    uctzar_out_after_fee = int(uctzar_out * 100 - fee)/100

    # Verify the pool has enough UCTZAR to fulfill the trade
    if uctzar_out_after_fee > pool_uctzar_balance:
        print("Insufficient UCTZAR in pool for this trade.")
        return

    # Print incoming ALGO and outgoing UCTZAR amounts
    #print(f"Incoming ALGO amount: {algo_amount} ALGO")
    #print(f"Outgoing UCTZAR amount: {uctzar_out_after_fee} UCTZAR (after fee)")

    lp_tokens_issued = 1_000_000 - check_balance(algod_client, accounts["liquidity_pool"]["address"], lp_asset_id, "LP-TOKEN")*100
    # lp1_tokens = check_balance(algod_client, accounts["liquidity_provider1"]["address"], lp_asset_id, "LP-TOKEN")
    # print("lp_1_tokens",lp1_tokens)
    lp1_share= check_balance(algod_client, accounts["liquidity_provider1"]["address"], lp_asset_id, "LP-TOKEN")*100 / lp_tokens_issued
    #print("lp_1_share",lp1_share)
    # lp2_tokens = check_balance(algod_client, accounts["liquidity_provider2"]["address"], lp_asset_id, "LP-TOKEN")
    # print("lp_2_tokens",lp2_tokens)
    lp2_share= check_balance(algod_client, accounts["liquidity_provider2"]["address"], lp_asset_id, "LP-TOKEN")*100 / lp_tokens_issued
    #print("lp_2_share",lp2_share)

    # Calculate fee distribution to liquidity providers based on their proportions
    lp1_fee = int(fee * lp1_share)
    lp2_fee = int(fee * lp2_share)

    # Atomic transaction: Trade ALGO for UCTZAR
    algo_txn = transaction.PaymentTxn(
        sender=trader_address,
        receiver=accounts["liquidity_pool"]["address"],
        amt=int(algo_amount * 1_000_000),  # Convert ALGO to microAlgos
        sp=params
    )

    uctzar_txn = AssetTransferTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=trader_address,
        amt=int(uctzar_out_after_fee*100),
        index=asset_id,
        sp=params
    )

    # Fee distribution transactions to liquidity providers
    lp1_fee_txn = AssetTransferTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=accounts["liquidity_provider1"]["address"],
        amt=int(lp1_fee),
        index=asset_id,
        sp=params
    )

    lp2_fee_txn = AssetTransferTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=accounts["liquidity_provider2"]["address"],
        amt=int(lp2_fee),
        index=asset_id,
        sp=params
    )

    # Group transactions and sign them
    gid = transaction.calculate_group_id([algo_txn, uctzar_txn, lp1_fee_txn, lp2_fee_txn])
    algo_txn.group = gid
    uctzar_txn.group = gid
    lp1_fee_txn.group = gid
    lp2_fee_txn.group = gid

    signed_algo_txn = algo_txn.sign(trader_private_key)
    signed_uctzar_txn = uctzar_txn.sign(accounts["liquidity_pool"]["private_key"])
    signed_lp1_fee_txn = lp1_fee_txn.sign(accounts["liquidity_pool"]["private_key"])
    signed_lp2_fee_txn = lp2_fee_txn.sign(accounts["liquidity_pool"]["private_key"])

    # Send grouped transactions
    txid = algod_client.send_transactions([signed_algo_txn, signed_uctzar_txn, signed_lp1_fee_txn, signed_lp2_fee_txn])
    transaction.wait_for_confirmation(algod_client, txid, 4)

    # Update pool balances based on the trade results
    pool_algo_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], None, "ALGO")-10
    pool_uctzar_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], uctzar_asset_id, "UCTZAR")

    return algo_amount, uctzar_out, uctzar_out_after_fee, lp1_fee, lp2_fee, pool_algo_balance, pool_uctzar_balance


def execute_trade_uctzar_to_algo(algod_client, trader_address, trader_private_key, uctzar_amount, asset_id, fee_percent=0.3):
    """
    Execute a trade where the trader exchanges UCTZAR for ALGOs from the liquidity pool.
    The fee is distributed proportionally to both liquidity providers.
    """
    params = algod_client.suggested_params()

    pool_algo_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], None, "ALGO")-10
    pool_uctzar_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], uctzar_asset_id, "UCTZAR")

    # Calculate the constant product k
    k = pool_algo_balance * pool_uctzar_balance
    
    # Calculate new balances after UCTZAR deposit
    new_uctzar_balance = pool_uctzar_balance + uctzar_amount/100
    new_algo_balance = k / new_uctzar_balance
    algo_out = pool_algo_balance - new_algo_balance
    
    # Deduct the trading fee (use fee_percent as a percentage)
    fee = algo_out * (fee_percent / 100)
    algo_out_after_fee = round(algo_out - fee, 6)  # Round to 6 decimal places for ALGO precision

    # Verify the pool has enough ALGOs to fulfill the trade
    if algo_out_after_fee > pool_algo_balance:
        print("Insufficient ALGO in pool for this trade.")
        return

    # Print incoming UCTZAR and outgoing ALGO amounts
    #print(f"Incoming UCTZAR amount: {uctzar_amount / 100:.2f} UCTZAR")  # Divide by 100 for 2 decimal places
    #print(f"Outgoing ALGO amount: {algo_out_after_fee} ALGO (after fee)")

    lp_tokens_issued = 1_000_000 - check_balance(algod_client, accounts["liquidity_pool"]["address"], lp_asset_id, "LP-TOKEN")*100
    #print("lp_tokens_issued",lp_tokens_issued)
    # lp1_tokens = check_balance(algod_client, accounts["liquidity_provider1"]["address"], lp_asset_id, "LP-TOKEN")
    # print("lp_1_tokens",lp1_tokens)
    lp1_share= check_balance(algod_client, accounts["liquidity_provider1"]["address"], lp_asset_id, "LP-TOKEN")*100 / lp_tokens_issued
    #print("lp_1_share",lp1_share)
    # lp2_tokens = check_balance(algod_client, accounts["liquidity_provider2"]["address"], lp_asset_id, "LP-TOKEN")
    # print("lp_2_tokens",lp2_tokens)
    lp2_share= check_balance(algod_client, accounts["liquidity_provider2"]["address"], lp_asset_id, "LP-TOKEN")*100 / lp_tokens_issued
    #print("lp_2_share",lp2_share)

    # Calculate fee distribution to liquidity providers based on their proportions
    lp1_fee = int(fee * lp1_share)
    lp2_fee = int(fee * lp2_share)

    # Calculate fee distribution to liquidity providers based on their proportions
    lp1_fee = round(fee * lp1_share, 6)
    lp2_fee = round(fee * lp2_share, 6)

    # Atomic transaction: Trade UCTZAR for ALGO
    uctzar_txn = AssetTransferTxn(
        sender=trader_address,
        receiver=accounts["liquidity_pool"]["address"],
        amt=int(uctzar_amount),  # Use UCTZAR amount directly in micro-units
        index=asset_id,
        sp=params
    )

    algo_txn = transaction.PaymentTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=trader_address,
        amt=int(algo_out_after_fee* 1_000_000),  # Convert ALGO to microAlgos
        sp=params
    )

    # Fee distribution transactions to liquidity providers
    lp1_fee_txn = transaction.PaymentTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=accounts["liquidity_provider1"]["address"],
        amt=int(lp1_fee * 1_000_000),  # Convert ALGO to microAlgos
        sp=params
    )

    lp2_fee_txn = transaction.PaymentTxn(
        sender=accounts["liquidity_pool"]["address"],
        receiver=accounts["liquidity_provider2"]["address"],
        amt=int(lp2_fee* 1_000_000),  # Convert ALGO to microAlgos
        sp=params
    )

    # Group transactions and sign them
    gid = transaction.calculate_group_id([uctzar_txn, algo_txn, lp1_fee_txn, lp2_fee_txn])
    uctzar_txn.group = gid
    algo_txn.group = gid
    lp1_fee_txn.group = gid
    lp2_fee_txn.group = gid

    signed_uctzar_txn = uctzar_txn.sign(trader_private_key)
    signed_algo_txn = algo_txn.sign(accounts["liquidity_pool"]["private_key"])
    signed_lp1_fee_txn = lp1_fee_txn.sign(accounts["liquidity_pool"]["private_key"])
    signed_lp2_fee_txn = lp2_fee_txn.sign(accounts["liquidity_pool"]["private_key"])

    # Send grouped transactions
    txid = algod_client.send_transactions([signed_uctzar_txn, signed_algo_txn, signed_lp1_fee_txn, signed_lp2_fee_txn])
    transaction.wait_for_confirmation(algod_client, txid, 4)

    pool_algo_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], None, "ALGO")-10
    pool_uctzar_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], uctzar_asset_id, "UCTZAR")   

    return uctzar_amount, algo_out, algo_out_after_fee, lp1_fee, lp2_fee, pool_algo_balance, pool_uctzar_balance

if __name__ == "__main__":

    # Mint UCTZAR stablecoin with total supply of 50 coins by creator
    uctzar_asset_id = create_uctzar_asset(algod_client, accounts["creator"]["address"], accounts["creator"]["private_key"])
    print("Successful UCTZAR mint", uctzar_asset_id)

    #Mint LP tokens which show the proportion each liquidity provider owns in the liquidity pool
    lp_asset_id = create_lp_token(
        algod_client,
        creator_address=accounts["liquidity_pool"]["address"],
        creator_private_key=accounts["liquidity_pool"]["private_key"]
    )
    print("Successful LP mint", lp_asset_id)

    # #All accounts opt in to receive UCTZAR stablecoins
    opt_in_to_asset(algod_client, accounts["liquidity_provider1"]["address"], accounts["liquidity_provider1"]["private_key"], uctzar_asset_id)
    opt_in_to_asset(algod_client, accounts["liquidity_provider2"]["address"], accounts["liquidity_provider2"]["private_key"], uctzar_asset_id)
    opt_in_to_asset(algod_client, accounts["liquidity_pool"]["address"], accounts["liquidity_pool"]["private_key"], uctzar_asset_id)
    opt_in_to_asset(algod_client, accounts["trader1"]["address"], accounts["trader1"]["private_key"], uctzar_asset_id)
    opt_in_to_asset(algod_client, accounts["trader2"]["address"], accounts["trader2"]["private_key"], uctzar_asset_id)
    print("Successful opt-in to receive UCTZAR")

    # Accounts opt in to receive LP tokens
    opt_in_to_asset(algod_client, accounts["liquidity_provider1"]["address"], accounts["liquidity_provider1"]["private_key"], lp_asset_id)
    opt_in_to_asset(algod_client, accounts["liquidity_provider2"]["address"], accounts["liquidity_provider2"]["private_key"], lp_asset_id)
    opt_in_to_asset(algod_client, accounts["liquidity_pool"]["address"], accounts["liquidity_pool"]["private_key"], lp_asset_id)
    print("Successful opt-in to receive LPTokes")

    # Transfer of UCTZAR to liquidity providers and traders
    transfer_asset(algod_client, accounts["creator"]["address"], accounts["creator"]["private_key"], accounts["liquidity_provider1"]["address"], 3000, uctzar_asset_id)
    transfer_asset(algod_client, accounts["creator"]["address"], accounts["creator"]["private_key"], accounts["liquidity_provider2"]["address"], 2000, uctzar_asset_id)
    transfer_asset(algod_client, accounts["creator"]["address"], accounts["creator"]["private_key"], accounts["trader1"]["address"], 2000, uctzar_asset_id)
    transfer_asset(algod_client, accounts["creator"]["address"], accounts["creator"]["private_key"], accounts["trader2"]["address"], 2000, uctzar_asset_id)
    print("Successful transfer of UCTZAR from creator to liquidity providers and traders")


    # Add liquidity providers add funds to liquidity pool and receive LP tokens in return
    add_liquidity(
        algod_client,
        provider_address=accounts["liquidity_provider1"]["address"],
        provider_private_key=accounts["liquidity_provider1"]["private_key"],
        algo_amount=15,  # 15 ALGOs
        uctzar_amount=3000,  # 30 UCTZAR (in micro-units)
        asset_id=uctzar_asset_id,
        lp_asset_id=lp_asset_id,
        lp_total_supply=1_000_000
    )
    
    # # Liquidity Provider 2 adds liquidity and receives LP tokens
    add_liquidity(
        algod_client,
        provider_address=accounts["liquidity_provider2"]["address"],
        provider_private_key=accounts["liquidity_provider2"]["private_key"],
        algo_amount=10,  # 30 ALGOs
        uctzar_amount=2000,  # 15 UCTZAR (in micro-units)
        asset_id=uctzar_asset_id,
        lp_asset_id=lp_asset_id,
        lp_total_supply=1_000_000
    )

    #Check initial pool balances
    pool_algo_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], None, "ALGO")-10
    pool_uctzar_balance = check_balance(algod_client, accounts["liquidity_pool"]["address"], uctzar_asset_id, "UCTZAR")
    print(f"Initial Pool ALGO Balance: {pool_algo_balance}")
    print(f"Initial Pool UCTZAR Balance: {pool_uctzar_balance}")

    #Perform first trade
    # Set parameters for the trade
    algo_amount_to_trade = 5  # The amount of ALGO the trader wants to exchange for UCTZAR
    trader_address = accounts["trader1"]["address"]
    trader_private_key = accounts["trader1"]["private_key"]
    asset_id = uctzar_asset_id  # This is the asset ID of UCTZAR
    # Call the function to execute the trade
    algo_amount, uctzar_out, uctzar_out_after_fee, lp1_fee, lp2_fee, pool_algo_balance, pool_uctzar_balance = execute_trade_algo_for_uctzar(
        algod_client=algod_client,
        trader_address=trader_address,
        trader_private_key=trader_private_key,
        algo_amount=algo_amount_to_trade,
        asset_id=asset_id,
        fee_percent=1  # Fee percentage, optional
    )

    print("Trade 1 Details:")
    print(f"ALGO Amount Traded: {algo_amount}")
    print(f"UCTZAR Amount Out: {uctzar_out}")
    print(f"UCTZAR Out After Fee: {uctzar_out_after_fee}")
    print(f"Liquidity Provider 1 Fee: {lp1_fee/100}")
    print(f"Liquidity Provider 2 Fee: {lp2_fee/100}")
    print(f"Updated Pool ALGO Balance: {pool_algo_balance}")
    print(f"Updated Pool UCTZAR Balance: {pool_uctzar_balance}")
    

    #Perform second trade
    # Set parameters for the trade
    uctzar_amount = 500  # The UCTZAR in cents to algos
    trader_address = accounts["trader2"]["address"]
    trader_private_key = accounts["trader2"]["private_key"]
    # Call the function to execute the trade
    uctzar_amount, algo_out, algo_out_after_fee, lp1_fee, lp2_fee, pool_algo_balance, pool_uctzar_balance = execute_trade_uctzar_to_algo(
        algod_client=algod_client,
        trader_address=trader_address,
        trader_private_key=trader_private_key,
        uctzar_amount=uctzar_amount,
        asset_id=asset_id,
        fee_percent=1  # Fee percentage, optional
    )
    # Print each returned value
    print("Trade 2 Details:")
    print(f"UCTZAR Amount Traded: {uctzar_amount/100} UCTZAR")  # Divide by 100 for cents to UCTZAR
    print(f"ALGO Amount Out: {algo_out}")
    print(f"ALGO Out After Fee: {algo_out_after_fee}")
    print(f"Liquidity Provider 1 Fee: {lp1_fee} ALGO")
    print(f"Liquidity Provider 2 Fee: {lp2_fee} ALGO")
    print(f"Updated Pool ALGO Balance: {pool_algo_balance}")
    print(f"Updated Pool UCTZAR Balance: {pool_uctzar_balance}")
