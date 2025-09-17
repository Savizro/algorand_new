from algosdk import transaction as tx  # type: ignore
from common import ALGOD, acct, sp, wait

ASSET_ID = 0             # <-- set to your BATCH_ASA_ID or UNIT_NFT_ID
RECEIVER_KEY = "pharmacy"  # or "consumer"
AMOUNT = 1               # 1 for NFT; n units for ASA

def opt_in(receiver_addr, receiver_sk, asset_id):
    params = sp()
    txn = tx.AssetTransferTxn(sender=receiver_addr, sp=params,
                              receiver=receiver_addr, amt=0, index=asset_id)
    stx = txn.sign(receiver_sk)
    try:
        txid = ALGOD.send_transaction(stx)
        wait(txid)
        print("Opt-in done for", receiver_addr)
    except Exception as e:
        if "has already opted in to asset" in str(e):
            print("Already opted-in")
        else:
            raise

def main():
    creator_addr, creator_sk = acct("creator")
    recv_addr, recv_sk = acct(RECEIVER_KEY)

    opt_in(recv_addr, recv_sk, ASSET_ID)

    params = sp()
    txn = tx.AssetTransferTxn(sender=creator_addr, sp=params,
                              receiver=recv_addr, amt=AMOUNT, index=ASSET_ID)
    stx = txn.sign(creator_sk)
    txid = ALGOD.send_transaction(stx)
    res = wait(txid)
    print(f"Transferred {AMOUNT} of {ASSET_ID} to {recv_addr} in round {res['confirmed-round']}")

if __name__ == "__main__":
    main()
