# PharmTrace — README

**Project:** PharmTrace — AI + Algorand powered verified medicine supply chain

**Team:** XENCRUIT — Debangshu Chatterjee, Aryan Sengupta, Aryan Saha, Diptomoy Das

---

## Overview

PharmTrace is a demo/reference implementation that demonstrates how to combine:

* **Algorand (ASA + NFT)** for immutable, eco-friendly asset tracking
* **Python (algosdk)** scripts to mint ASAs (batches) and NFTs (package-level IDs)
* **Flask** API for QR-verification + logging AI-detection results to the blockchain
* **LLaMA 4 Vision / LoRA / VLM pipeline** to inspect packaging images and produce counterfeit detection evidence
* **React + Next.js** dashboard to visualize the medicine journey and verification results

This repository contains example scripts, Flask endpoints, Next.js code snippets, and operational notes so you can run an end-to-end demo on Algorand TestNet or in a local Algorand Sandbox.

---

## Repository layout (recommended)

```
/pharmtrace
  /backend
    mint_asset.py           # Python demo: ASA + NFT minting (algosdk)
    qr_generator.py         # Generates QR codes for minted packages
    flask_api.py            # Flask server: verify QR, receive AI evidence, log hash to Algorand
    requirements.txt        # pip dependencies
    utils.py                # helper functions (hashing, algod client helper)
  /frontend
    /pharmtrace-dashboard   # Next.js + React dashboard
      pages/
      components/
      package.json
  /docs
    PharmTrace_README.md    # this file
  /scripts
    run-local.sh            # convenience script to bring containers up (optional)

```

---

## High-level flow (how it works)

1. Manufacturer runs `mint_asset.py` to create a **batch ASA** and optionally **NFTs** for each package. Each package NFT contains a unique token-id and metadata (e.g., batch, expiry, product info). The script prints the `asset_id` and transaction ID.
2. `qr_generator.py` builds a QR code for each package which encodes a verification URL like:

   ```text
   https://your-backend.example.com/verify?asset_id={ASSET_ID}&package={NFT_ID}
   ```

   or a compact Algorand URI `algorand://{asset_id}?tx={txid}` for dapp-style clients.
3. End consumer (or retailer) scans the QR. The client calls the Flask verification API. The API first checks the blockchain (Indexer/Algod) to confirm ownership, asset metadata, and registration.
4. The client app optionally sends an **image of the packaging** to the AI pipeline (LLaMA 4 Vision) to verify the packaging — this runs either locally or as a separate inference service (GROQ / dedicated GPU). The AI returns a structured result (labels, confidence, bounding boxes, and a short report).
5. The backend computes a **SHA-256** hash of the AI result and stores that hash immutably on Algorand (either by attaching it as a `note` in a payment/asset transfer transaction, or as part of an asset reconfigure or separate logging transaction). The backend returns verification result and the Algorand transaction ID for audit.
6. The React dashboard consumes backend APIs and displays the full supply chain timeline (manufacturer → distributor → retailer → consumer), ASA/NFT details, and AI authenticity checks (with links to Algorand TXIDs / indexer queries).

---

## Prerequisites

* Docker (for Algorand Sandbox) OR a PureStake API key (TestNet) or your own Algorand node
* Python 3.9+ (3.10 recommended)
* Node.js 18+ and npm or pnpm for the Next.js frontend
* Access to the `py-algorand-sdk` (install via pip)
* A LLaMA 4 Vision / VLM inference endpoint (or any image classification model) — the README demonstrates how to connect results, not how to train LLaMA 4 Vision.

### Useful references

* Algorand Sandbox: quick local algorand environment and indexer. See the official sandbox docs for `./sandbox up`. citeturn0search11
* ASA + NFT developer guides on Algorand Developer Portal. citeturn0search1turn0search2
* Writing / reading the transaction `note` field (used to store hashes) on Algorand. citeturn0search4
* Connecting via PureStake (if you want to use a hosted node). citeturn0search5
* ARC-0003 for NFT metadata conventions on Algorand. citeturn0search18

---

## Environment & configuration

Create a `.env` file for local development (backend). Example:

```
# Algod / Indexer
ALGOD_ADDRESS=http://localhost:4001
ALGOD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
INDEXER_ADDRESS=http://localhost:8980
INDEXER_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# If using PureStake instead, set these:
# ALGOD_ADDRESS=https://testnet-algorand.api.purestake.io/ps2
# ALGOD_TOKEN=<YOUR_PURESTAKE_KEY>
# PURESTAKE_HEADER_NAME='X-API-Key'

# Account
MANUFACTURER_MNEMONIC="your 25-word mnemonic here"

# Optional: IPFS or object storage base URL where you pin metadata
IPFS_GATEWAY=https://ipfs.io/ipfs/

# Flask
FLASK_PORT=5000
```

> **Note:** For sandbox, the default algod token is `aaaaaaaa...` and endpoints are given by the sandbox README. When using PureStake, follow their guide and place your API key in the `ALGOD_TOKEN` and set the proper header when creating the client. citeturn0search11turn0search5

---

## Backend: Python demo scripts

Install Python dependencies (example `backend/requirements.txt`):

```
flask
py-algorand-sdk
python-dotenv
qrcode[pil]
requests
pillow
```

Run:

```bash
python -m pip install -r backend/requirements.txt
```

### 1) `mint_asset.py` — Example ASA + NFT minting script (Python/algosdk)

Below is a compact, annotated snippet. Save as `backend/mint_asset.py`.

```python
# backend/mint_asset.py
import json
import base64
import hashlib
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn
from algosdk.future.transaction import PaymentTxn

# Helper: build algod client from env (set ALGOD_ADDRESS / ALGOD_TOKEN)
from utils import get_algod_client, recover_private_key_from_mnemonic

ALGOD = get_algod_client()

def create_asset(creator_addr, creator_pk, unit_name, asset_name, total, decimals, url, metadata_json_bytes=None):
    params = ALGOD.suggested_params()

    # If metadata_json_bytes present, create a sha256 metadata hash (32 bytes)
    metadata_hash = None
    if metadata_json_bytes is not None:
        metadata_hash = hashlib.sha256(metadata_json_bytes).digest()

    txn = AssetConfigTxn(
        sender=creator_addr,
        sp=params,
        total=total,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=creator_addr,
        reserve=creator_addr,
        freeze=creator_addr,
        clawback=creator_addr,
        url=url,
        decimals=decimals,
        metadata_hash=metadata_hash,
    )

    stxn = txn.sign(creator_pk)
    txid = ALGOD.send_transaction(stxn)
    print('Sent asset creation txid', txid)
    confirmed = wait_for_confirmation(ALGOD, txid)
    asset_id = confirmed['asset-index']
    print('Created asset with id', asset_id)
    return asset_id, txid


def wait_for_confirmation(client, txid, timeout=10):
    last_round = client.status().get('last-round')
    start_round = last_round + 1
    current_round = start_round
    for _ in range(timeout):
        try:
            pt = client.pending_transaction_info(txid)
            if pt.get('confirmed-round', 0) > 0:
                return pt
        except Exception:
            pass
        current_round += 1
        client.status_after_block(current_round)
    raise Exception('Transaction not confirmed')


if __name__ == '__main__':
    # load from env or local file
    from dotenv import load_dotenv
    import os
    load_dotenv()
    MANU_MNEMONIC = os.environ['MANUFACTURER_MNEMONIC']
    pk = recover_private_key_from_mnemonic(MANU_MNEMONIC)
    addr = account.address_from_private_key(pk)

    # Example: create batch ASA (SFT-like)
    metadata = {
        "name": "Paracetamol 500mg - Batch 2025A",
        "manufacturer": "ACME Pharma",
        "batch": "2025A",
        "expiry": "2026-08-31",
        "schema": "ARC-0003"
    }
    metadata_bytes = json.dumps(metadata).encode('utf-8')

    asset_id, txid = create_asset(
        creator_addr=addr,
        creator_pk=pk,
        unit_name='PCT500',
        asset_name='Paracetamol-2025A',
        total=100000,        # batch amount
        decimals=0,
        url='https://ipfs.io/ipfs/<metadata_cid_or_http_url>',
        metadata_json_bytes=metadata_bytes,
    )
    print('Asset ID:', asset_id)

    # To create a pure NFT for a single package, set total=1 and decimals=0
```

> The above script: creates an ASA and optionally attaches a `metadata_hash` (SHA-256 of JSON) that follows ARC-3 conventions.

### 2) `qr_generator.py` — create verification QR codes

```python
# backend/qr_generator.py
import qrcode

def generate_qr(verify_url, out_path):
    qr = qrcode.QRCode(version=2, box_size=8, border=4)
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(out_path)

if __name__ == '__main__':
    url = 'https://localhost:5000/verify?asset_id=12345&package=67890'
    generate_qr(url, 'sample_pkg_qr.png')
```

### 3) `flask_api.py` — QR verification + AI evidence logging

Key endpoints:

* `GET /verify` - takes query params `asset_id` and `package` (npm\_id) and returns blockchain metadata and current owner/opt-in status
* `POST /ai-evidence` - accepts JSON `{asset_id, package, ai_result}` where `ai_result` is the JSON output from LLaMA 4 Vision. The server will compute SHA-256 on the `ai_result` JSON string, store that hash in a short blockchain transaction `note`, and return the resulting txid for audit.

```python
# backend/flask_api.py
from flask import Flask, request, jsonify
import json, hashlib, base64, os
from algosdk.v2client import algod, indexer
from algosdk.future.transaction import PaymentTxn
from utils import get_algod_client, wait_for_confirmation, recover_private_key_from_mnemonic

app = Flask(__name__)
ALGOD = get_algod_client()
INDEXER = None  # optional: create indexer client if you run sandbox indexer

MANU_MNEMONIC = os.environ.get('MANUFACTURER_MNEMONIC')
MANU_PK = recover_private_key_from_mnemonic(MANU_MNEMONIC)
MANU_ADDR = None

# Optional: load address from pk
from algosdk import account
MANU_ADDR = account.address_from_private_key(MANU_PK)

@app.route('/verify')
def verify():
    asset_id = request.args.get('asset_id')
    package = request.args.get('package')
    if not asset_id:
        return jsonify({'error': 'asset_id required'}), 400

    # basic verification via algod/indexer
    try:
        acct_info = ALGOD.account_info(MANU_ADDR)
        # in production: query Indexer for asset info and supply chain history
        # Here: get asset info
        asset_info = ALGOD.asset_info(int(asset_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'asset_info': asset_info})

@app.route('/ai-evidence', methods=['POST'])
def ai_evidence():
    payload = request.get_json()
    asset_id = payload.get('asset_id')
    package = payload.get('package')
    ai_result = payload.get('ai_result')  # JSON-like

    if not ai_result:
        return jsonify({'error': 'ai_result required'}), 400

    # canonicalize & hash
    ai_json = json.dumps(ai_result, sort_keys=True, separators=(',', ':')).encode('utf-8')
    evidence_hash = hashlib.sha256(ai_json).digest()  # 32 bytes

    # attach the hash into a payment txn note field to store on-chain
    params = ALGOD.suggested_params()
    # small payment to self to create transaction; in production use dedicated log account
    txn = PaymentTxn(sender=MANU_ADDR, sp=params, receiver=MANU_ADDR, amt=1000, note=evidence_hash)
    stxn = txn.sign(MANU_PK)
    txid = ALGOD.send_transaction(stxn)
    confirmed = wait_for_confirmation(ALGOD, txid)

    return jsonify({'status': 'logged', 'txid': txid, 'hash_hex': evidence_hash.hex()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('FLASK_PORT', 5000)), debug=True)
```

**Notes:**

* Storing large AI results on-chain is expensive; instead we store a compact SHA-256 commitment on-chain and push the detailed evidence to IPFS or your secure object store. Include the IPFS CID in the transaction note or as an asset metadata URL.
* The example uses a small self-payment to create a transaction; in production, use a dedicated logging/accounting flow and consider paying with a fee-only transaction or group transactions.

---

## LLaMA 4 Vision integration (AI detection) — how to connect

**Goal:** Use LLaMA 4 Vision (or any VLM) to analyze an image and return a structured result (labels, confidences, bounding boxes, textual explanation). Then compute a SHA-256 hash of that structured result and commit it to Algorand.

1. **Run inference** — your LLaMA 4 Vision endpoint (self-hosted or provider) returns JSON like:

```json
{
  "label": "authentic",
  "confidence": 0.94,
  "explanations": ["hologram matches template", "font/spacing matches"],
  "detections": [{"class":"hologram","score":0.96,"bbox":[10,20,200,80]}]
}
```

2. **Canonicalize and hash** — `hash = sha256(json.dumps(result, sort_keys=True).encode('utf-8'))`.
3. **Log on-chain** — as in the Flask `ai-evidence` endpoint, store the `hash` in a transaction `note`.
4. **Audit** — the transaction ID (`txid`) proves that at a given block time, this hash was recorded. The detailed evidence is retrievable from IPFS or your object store and can be checked by computing the hash locally and verifying it matches the recorded hash.

**Security & integrity notes:**

* Sign AI evidence payloads on the client-side where possible before sending. This reduces chances of tampering between client and server.
* Keep private keys in secure vaults. For production consider a KMS/HSM or Algorand Key Management (KMD) solution.

---

## Frontend: Next.js React dashboard (high-level)

**Purpose:** Display the medicine journey, ASA/NFT metadata, and recent verification events.

**Key pages/components:**

* `pages/index.tsx` — Overview & search by QR or asset id
* `components/AssetDetails.tsx` — fetches `/verify?asset_id=...` and shows asset metadata, metadata IPFS link, asset creator, total supply
* `components/JourneyTimeline.tsx` — visual timeline with events (mint, distributor transfer events, retailer opt-ins, consumer verifications). Each event includes a TXID with link to Algorand Explorer or Sandbox Indexer.
* `components/AuthenticityCheck.tsx` — allow uploading an image to the AI endpoint; display model output and TXID linking to the logged evidence.

**Sample fetch** (client → backend):

```ts
// fetch asset details
async function fetchAsset(assetId: number) {
  const res = await fetch(`/api/verify?asset_id=${assetId}`);
  return res.json();
}

// post AI evidence
async function postEvidence(assetId:number, packageId:number, aiResult:any) {
  const res = await fetch('/api/ai-evidence', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({asset_id: assetId, package: packageId, ai_result: aiResult})
  });
  return res.json();
}
```

**Deploying the frontend** — you can host Next.js on Vercel, Netlify, or your own node. For local testing:

```
cd frontend/pharmtrace-dashboard
npm install
npm run dev
```

---

## Running locally (quickstart)

1. Option A — **Local sandbox (recommended for testing)**

   * Install Docker and clone Algorand sandbox: `git clone https://github.com/algorand/sandbox.git` (see sandbox docs). Run `./sandbox up` to bring up local algod + indexer. citeturn0search11
   * Set `.env` tokens (sandbox uses the well-known `aaaaaaaa...` token in many configs)

2. Option B — **TestNet via PureStake**

   * Create an account on PureStake, get an API key, and set `ALGOD_ADDRESS` and `ALGOD_TOKEN` accordingly. See the PureStake / Algorand tutorial. citeturn0search5

3. Start backend

```
cd backend
export FLASK_APP=flask_api.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
```

4. Mint a batch (example)

```
python mint_asset.py
```

5. Generate QR for a package

```
python qr_generator.py
```

6. Start frontend (Next.js)

```
cd frontend/pharmtrace-dashboard
npm install
npm run dev
```

---

## Testing & verification scenarios

* **Happy path:** Mint ASA + NFTs; consumer scans QR; verification returns `authentic: true` (AI result hash matches; metadata matches on-chain asset).
* **Tampered package:** AI reports mismatch; `ai-evidence` stores hash; transaction visible on Algorand. Dashboard shows history and flags package.
* **Recall simulation:** Manufacturer reconfigures asset metadata to mark recall (AssetConfigTxn reconfigure) and dashboard highlights recalled batch.

---

## Production considerations & hardening

* **Key management:** Use KMS / HSM. Never store mnemonics in plaintext. Consider Algorand `kmd` or an external KMS.
* **Costs:** Storing large metadata on-chain is wasteful. Use IPFS and store CID on-chain. Only store compact commitments (sha256) on-chain.
* **Scale:** Use grouped transactions and TEAL smart contracts for complex business logic like multi-party approvals or automated recalls.
* **Privacy:** Hash personally identifiable evidence; store raw evidence off-chain.
* **Monitoring:** Run Indexer for fast queries and build a small audit dashboard that shows tx status and block times.

---

## Troubleshooting

* If `algod` calls fail, check your `ALGOD_ADDRESS` and `ALGOD_TOKEN` and ensure the sandbox is `up` or the PureStake key is valid.
* If asset creation returns `asset-index` missing, the transaction may not have confirmed — check pending transaction info and increase `wait_for_confirmation` timeout.

---

## Further reading / references

* Algorand Sandbox (local node + indexer). citeturn0search11
* Working with ASA in Python. citeturn0search1
* How to create NFTs on Algorand. citeturn0search2
* Read & write to transaction note field (store hashes). citeturn0search4
* PureStake API example (connecting Python SDK). citeturn0search5
* ARC-3 metadata / NFT conventions. citeturn0search18

---

## License & attribution

This demo/README is provided for educational/demo purposes. Review Algorand policies and legal requirements if you plan to build a production medical supply chain product.

---

## What I included for you

I created a complete README covering: architecture, dependencies, demo scripts for minting ASA/NFTs, Flask verification + AI evidence logging (hashing + storing on-chain), QR generation notes, and the high-level Next.js dashboard integration. The repository layout above suggests where to place each script.

---

*End of README*
