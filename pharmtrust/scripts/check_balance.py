from common import ALGOD, acct
addr, _ = acct("creator")
bal = ALGOD.account_info(addr)["amount"] / 1e6
print(addr, f"{bal} ALGO")
