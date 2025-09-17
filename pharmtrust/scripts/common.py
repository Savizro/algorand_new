import json
from pathlib import Path
from algosdk import account, mnemonic  # type: ignore
from algosdk.v2client import algod  # type: ignore

ROOT = Path(__file__).resolve().parents[2]  # Go up to the root directory
CONF = json.loads((ROOT / "config" / "accounts.json").read_text())

ALGOD = algod.AlgodClient(CONF["network"]["algod_token"], CONF["network"]["algod_address"])

def acct(key: str):
    m = CONF[key]["mnemonic"]
    a = CONF[key]["address"]
    sk = mnemonic.to_private_key(m)
    addr = account.address_from_private_key(sk)
    assert addr == a, f"Address mismatch for {key}: config {a} vs derived {addr}"
    return addr, sk

def sp():
    return ALGOD.suggested_params()

def wait(txid: str, timeout=10):
    last = ALGOD.status().get("last-round")
    start = last
    while last < start + timeout:
        res = ALGOD.pending_transaction_info(txid)
        if res.get("confirmed-round", 0) > 0:
            return res
        last += 1
        ALGOD.status_after_block(last)
    raise TimeoutError(f"Tx {txid} not confirmed in {timeout} rounds")

# common.py
import json
from pathlib import Path

def write_artifact(key: str, value):
    """Persist minted IDs to artifacts.json at project root."""
    path = Path(__file__).resolve().parents[1] / "artifacts.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text() or "{}")
        except Exception:
            data = {}
    data[key] = value
    path.write_text(json.dumps(data, indent=2))

