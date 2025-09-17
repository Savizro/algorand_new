# scripts/create_batch_asa.py
import json
from pathlib import Path
from algosdk import transaction as tx

from common import ALGOD, acct, sp, wait, write_artifact, ROOT

def main():
    creator_addr, creator_sk = acct("creator")
    assert creator_sk, "creator mnemonic is required to mint"

    # Optional: read metadata for nicer names
    meta_path = ROOT / "metadata" / "batch.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    unit_name  = meta.get("unit_name", "AMX500")
    asset_name = meta.get("name", "PharmaTrust Batch")
    url        = meta.get("url", "")  # e.g. ipfs://CID/batch.json
    total      = int(meta.get("total", 1000))
    note_bytes = json.dumps(meta).encode() if meta else None

    params = sp()
    txn = tx.AssetCreateTxn(
        sender=creator_addr,
        sp=params,
        total=total,
        decimals=0,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        url=url,
        manager=creator_addr,
        reserve=creator_addr,
        freeze=creator_addr,
        clawback=creator_addr,
        note=note_bytes,
    )
    stx = txn.sign(creator_sk)
    txid = ALGOD.send_transaction(stx)
    res = wait(txid)
    asset_id = res["asset-index"]
    print("BATCH_ASA_ID:", asset_id)
    write_artifact("BATCH_ASA_ID", asset_id)

if __name__ == "__main__":
    main()
