# ================================
# 🚀 PHTR Token Creator + microAlgo Test Transfer
# ================================

# 1️⃣ Install SDK if not already installed
# pip install py-algorand-sdk

from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk.transaction import AssetConfigTxn, PaymentTxn
import time

# ------------------------
# 2️⃣ Connect to AlgoNode TestNet
# ------------------------
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # Public endpoint, no key needed

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
print("Connected to TestNet ✅")
print("Node Status:", algod_client.status())

# ------------------------
# 3️⃣ Your Lute/TestNet Wallet
# ------------------------
MNEMONIC = "cover pave ramp vocal genuine unable limb outdoor humble bamboo series twelve onion royal upon leisure slow wire camera glove crazy defy entire able various"
private_key = mnemonic.to_private_key(MNEMONIC)
public_address = account.address_from_private_key(private_key)
print("Wallet Address:", public_address)

# ------------------------
# 4️⃣ Token Parameters
# ------------------------
ASSET_NAME = "PHTR"
UNIT_NAME = "PHTR"
TOTAL_SUPPLY = 1000000
DECIMALS = 0
IMAGE_URL = "https://tinyurl.com/y4y9upsv"

# ------------------------
# 5️⃣ Create Token Transaction
# ------------------------
params = algod_client.suggested_params()

txn = AssetConfigTxn(
    sender=public_address,
    sp=params,
    total=TOTAL_SUPPLY,
    default_frozen=False,
    unit_name=UNIT_NAME,
    asset_name=ASSET_NAME,
    manager=public_address,
    reserve=public_address,
    freeze=public_address,
    clawback=public_address,
    decimals=DECIMALS,
    url=IMAGE_URL,
    note="PHTR Token TestNet".encode(),
)

signed_txn = txn.sign(private_key)
txid = algod_client.send_transaction(signed_txn)
print("Token creation transaction sent! TXID:", txid)

# ------------------------
# 6️⃣ Wait for Token Confirmation
# ------------------------
def wait_for_confirmation(client, txid):
    print("Waiting for confirmation...")
    while True:
        tx_info = client.pending_transaction_info(txid)
        if tx_info.get("confirmed-round", 0) > 0:
            print("Transaction confirmed in round", tx_info["confirmed-round"])
            return tx_info
        time.sleep(2)

tx_info = wait_for_confirmation(algod_client, txid)
asset_id = tx_info["asset-index"]
print(f"✅ Your PHTR Token is created on TestNet!")
print(f"Asset ID: {asset_id}")
print(f"Token Name: {ASSET_NAME} | Unit Name: {UNIT_NAME} | Total Supply: {TOTAL_SUPPLY}")
print(f"Token Image URL: {IMAGE_URL}")

# ===========================
# 7️⃣ Simple microAlgo Transfer
# ===========================
def micro_algo_transfer(sender_pk, sender_addr, receiver_addr, amount=1000):
    """Send microAlgos (default 1000 microAlgos) to another address"""
    params = algod_client.suggested_params()
    txn = PaymentTxn(sender_addr, params, receiver_addr, amount)
    signed_txn = txn.sign(sender_pk)
    txid = algod_client.send_transaction(signed_txn)
    print(f"MicroAlgo transfer sent! TXID: {txid}")

    tx_info = wait_for_confirmation(algod_client, txid)
    print(f"✅ MicroAlgo transfer confirmed in round {tx_info['confirmed-round']}")
    print(f"Sent {amount} microAlgos to {receiver_addr}")

# ------------------------
# 8️⃣ Execute Test Transfer
# ------------------------
TEST_RECEIVER = "FG3DHJKSYVS5LWJXKD646SJXHN5UZN6UE2G3PMXQYNLVNVPUMLJ3LHEFV4"  # Replace with a TestNet address
micro_algo_transfer(private_key, public_address, TEST_RECEIVER, amount=1000)
