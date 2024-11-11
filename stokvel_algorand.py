from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import Multisig, PaymentTxn, MultisigTransaction
import time
import random


####################

#Set Algod Client Which Enable Interaction with the Algorand Testnet

algod_address = "https://testnet-api.4160.nodely.dev"
algod_token = ""

def get_algod_client():
    return algod.AlgodClient(algod_token, algod_address)

#####################

#Was used to create accounts and store their wallet adresses and private keys
#Account swas pre-funded using the Testnet Dispenser

# Function to create multiple test accounts and format the output
# def create_test_accounts(num_accounts=5):
#     member_addresses = []
#     member_accounts = []

#     for _ in range(num_accounts):
#         private_key, address = account.generate_account()
#         member_addresses.append(address)
        
#         # Store the account details as a dictionary
#         member_accounts.append({"address": address, "private_key": private_key})

#         print("Account Address:", address)
#         print("Account Mnemonic:", mnemonic.from_private_key(private_key))
    
#     # Print formatted output
#     print("\n# List of member addresses")
#     print("member_addresses = [")
#     for address in member_addresses:
#         print(f'    "{address}",')
#     print("]\n")
    
#     print("# Placeholder member accounts with private keys")
#     print("member_accounts = [")
#     for acc in member_accounts:
#         print(f'    {{"address": "{acc["address"]}", "private_key": "{acc["private_key"]}"}},')
#     print("]")
    
#     return member_addresses, member_accounts

###################3

# List of member addresses
member_addresses = [
    "FR5O56XUKQUWKR4MCHZLUG6WPJVMF3BO5WWWKUZRXZX2SYTKZITQOUYI4A",
    "LWKCK5MEG25L7HAMTENV73XWPDB5JAJDEWQNZBWJEFOXFVZ463D74ONG5I",
    "2364YVHPJKK422CWSZLD32S67WW7Z53TGMA5KPH3PVAXG5LZZSYRH2SBZM",
    "TWOENTCBDJT7RVCPNMBG6D6IA7PUM3SFGVRSGTM46CQCUA66NXMQBBYCYY",
    "7MES653OW4L5MSP7ABE7A7QM5CUAMGJFGAVZEV5LHVTLXZB2LGN7HKXIKM",
]

# List of member adresses and their corresponding private keys
member_accounts = [
    {"address": "FR5O56XUKQUWKR4MCHZLUG6WPJVMF3BO5WWWKUZRXZX2SYTKZITQOUYI4A", "private_key": "wta+FtKreNRAb/OQpOuCobwfi8pbZfhMXBxTV9LQhQYseu769FQpZUeMEfK6G9Z6asLsLu2tZVMxvm+pYmrKJw=="},
    {"address": "LWKCK5MEG25L7HAMTENV73XWPDB5JAJDEWQNZBWJEFOXFVZ463D74ONG5I", "private_key": "pxw/A6OFahGK5loWaMhHEMCd3YGijohIqt4c9ROjNuVdlCV1hDa6v5wMmRtf7vZ4w9SBIyWg3IbJIV1y1zz2xw=="},
    {"address": "2364YVHPJKK422CWSZLD32S67WW7Z53TGMA5KPH3PVAXG5LZZSYRH2SBZM", "private_key": "n8S7uucz/R/UGFc5uqFD2d/K/82SLnOmpLnyO5OPIv/W/cxU70qVzWhWllY96l79rfz3czMB1Tz7fUFzdXnMsQ=="},
    {"address": "TWOENTCBDJT7RVCPNMBG6D6IA7PUM3SFGVRSGTM46CQCUA66NXMQBBYCYY", "private_key": "M7R31vBeDKvilChL0/EKsu9pO/I+QBP0262aluYbCKednEbMQRpn+NRPawJvD8gH30ZuRTVjI02c8KAqA95t2Q=="},
    {"address": "7MES653OW4L5MSP7ABE7A7QM5CUAMGJFGAVZEV5LHVTLXZB2LGN7HKXIKM", "private_key": "cCofQ2GUNklxQYRO4TD7r76f5OxL5HgOcXiZmuDK5Wv7CS93brcX1kn/AEnwfgzoqAYZJTArklerPWa75DpZmw=="},
]

# Extract private keys for easy reference in signing transactions
private_keys = [account["private_key"] for account in member_accounts]

#######################

#Creation of multisig account where 4 out of 5 signatures is required to make a transaction

def create_multisig_account():
    multisig = Multisig(version=1, threshold=4, addresses=member_addresses)
    print("Multisig Address:", multisig.address())
    return multisig

#######################

#Deposit of 5 Algos from individual wallets to multisig account

def deposit_to_multisig(algod_client, sender_private_key, sender_address, multisig_address):
    params = algod_client.suggested_params()
    amount = 5 * 1_000_000  # 5 Algos in microAlgos
    txn = PaymentTxn(sender_address, params, multisig_address, amount)
    signed_txn = txn.sign(sender_private_key)

    try:
        txid = algod_client.send_transaction(signed_txn)
        print(f"Transaction sent with txID: {txid}")
        wait_for_confirmation(algod_client, txid)
        print(f"Deposit of 5 Algos from {sender_address} to multisig account {multisig_address} confirmed.")
    except Exception as e:
        print(f"Failed to send transaction from {sender_address}: {e}")

# This wait function ensures that a transaction has been submitted on the blockchain before proceeding
def wait_for_confirmation(client, txid):
    while True:
        try:
            tx_info = client.pending_transaction_info(txid)
            if tx_info.get("confirmed-round", 0) > 0:
                print("Transaction confirmed in round", tx_info["confirmed-round"])
                return tx_info
        except Exception:
            pass
        time.sleep(1)

################################

#Function to perform payout from multisig account to a selected recipient

def payout_from_multisig(algod_client, multisig, recipient_address, private_keys):
    params = algod_client.suggested_params()
    amount = 15 * 1_000_000  # 15 Algos in microAlgos

    # Create the payment transaction
    msig_pay = PaymentTxn(multisig.address(), params, recipient_address, amount, note=b"Multisig Payment")

    # Create the multisig transaction
    msig_txn = MultisigTransaction(msig_pay, multisig)

    # 4 Accounts signoff on transaction
    msig_txn.sign(private_keys[0])
    msig_txn.sign(private_keys[1])
    msig_txn.sign(private_keys[2])
    msig_txn.sign(private_keys[3])

    try:
        # Send the signed transaction
        txid = algod_client.send_transaction(msig_txn)
        wait_for_confirmation(algod_client, txid)
        print(f"Payout of 15 Algos to {recipient_address} confirmed.")
    except Exception as e:
        print(f"Failed to send payout transaction: {e}")

##########################


# Function to randomly select a recipient who has not yet received a payout
def select_random_recipient():
    available_members = list(set(member_addresses) - paid_members)
    recipient = random.choice(available_members)
    paid_members.add(recipient)
    return recipient

###########################

#Main programme to initiates creation of the Algorand client, creates a new multisig, 
#Cycles through 5 iterations of payments to a multisig account from 5 indiviual accounts
#Then payout is conducted at the end of the period to a randomly selected account

if __name__ == "__main__":
    # Example usage
    algod_client = get_algod_client()
    #accounts = create_test_accounts(num_accounts=5)
    #fund accounts with dispenser
    multisig = create_multisig_account()
    multisig_address = multisig.address()
    paid_members = set()

    # Run a 5-month cycle
    for month in range(5):
        print(f"--- Month {month + 1} ---")
        
        # Reset paid members at the start of a new cycle
        if month == 0:
            paid_members.clear()
        
        # Perform the monthly deposit cycle where each member deposits 5 Algos to the multisig account
        for member in member_accounts:
            deposit_to_multisig(algod_client, member["private_key"], member["address"], multisig_address)

        # Select a recipient and execute the payout from  multisig account
        recipient_address = select_random_recipient()
        payout_from_multisig(algod_client, multisig, recipient_address, private_keys)

        print(f"End of Month {month + 1}\n")




