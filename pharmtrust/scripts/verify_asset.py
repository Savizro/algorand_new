from common import ALGOD, acct

ASSET_ID = 0  # set to your asset id

def bal(addr, asset_id):
    ai = ALGOD.account_info(addr)
    for a in ai.get("assets", []):
        if a["asset-id"] == asset_id:
            return a["amount"]
    return 0

def main():
    creator_addr, _ = acct("creator")
    print("Creator:", creator_addr, "bal:", bal(creator_addr, ASSET_ID))
    asset = ALGOD.asset_info(ASSET_ID)
    print("Asset params:", asset["params"])

if __name__ == "__main__":
    main()
