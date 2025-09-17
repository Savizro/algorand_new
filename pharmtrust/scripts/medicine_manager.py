import json
from pathlib import Path
from common import ALGOD, acct, sp, wait
from algosdk import transaction as tx  # type: ignore
from datetime import datetime
import uuid

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_FILE = ROOT / "pharmtrust" / "artifacts.json"

class MedicineManager:
    def __init__(self):
        self.artifacts = self.load_artifacts()
        self.creator_addr, self.creator_sk = acct("creator")
    
    def load_artifacts(self):
        """Load existing artifacts from JSON file"""
        try:
            with open(ARTIFACTS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"medicines": {}}
    
    def save_artifacts(self):
        """Save artifacts to JSON file"""
        with open(ARTIFACTS_FILE, 'w') as f:
            json.dump(self.artifacts, f, indent=2)
    
    def generate_medicine_id(self, medicine_name, batch_no):
        """Generate unique medicine ID"""
        return f"{medicine_name}_{batch_no}_{datetime.now().strftime('%Y%m%d')}"
    
    def create_batch_asa(self, medicine_name, batch_no, total_units=1000, expiry_date="2027-08"):
        """Create a new batch ASA for a medicine"""
        medicine_id = self.generate_medicine_id(medicine_name, batch_no)
        
        print(f"Creating batch ASA for {medicine_name} - Batch {batch_no}")
        
        # Generate unique unit name and asset name (max 8 chars for unit_name)
        medicine_short = medicine_name.replace(' ', '')[:3].upper()
        batch_short = batch_no.replace('-', '')[-5:]  # Last 5 chars of batch
        unit_name = f"{medicine_short}{batch_short}"[:8]  # Ensure max 8 chars
        asset_name = f"{medicine_name}Batch-{batch_no}"
        
        # Create metadata URL (you'll need to upload to IPFS)
        batch_url = f"ipfs://QmYourCIDHere/batch_{medicine_id}.json"
        
        params = sp()
        txn = tx.AssetCreateTxn(
            sender=self.creator_addr, sp=params,
            total=total_units, decimals=0, default_frozen=False,
            unit_name=unit_name, asset_name=asset_name,
            url=batch_url,
            manager=self.creator_addr, reserve=self.creator_addr, 
            freeze=self.creator_addr, clawback=self.creator_addr,
        )
        
        stx = txn.sign(self.creator_sk)
        txid = ALGOD.send_transaction(stx)
        res = wait(txid)
        
        batch_asa_id = res["asset-index"]
        print(f"Batch ASA created: {batch_asa_id}")
        
        return batch_asa_id
    
    def create_unit_nft(self, medicine_name, batch_no, unit_serial):
        """Create a new unit NFT for a specific medicine unit"""
        medicine_id = self.generate_medicine_id(medicine_name, batch_no)
        
        print(f"Creating unit NFT for {medicine_name} - Unit {unit_serial}")
        
        # Generate unique unit name and asset name (max 8 chars for unit_name)
        medicine_short = medicine_name.replace(' ', '')[:3].upper()
        unit_name = f"{medicine_short}U{unit_serial}"[:8]  # Ensure max 8 chars
        asset_name = f"{medicine_name} Unit #{unit_serial}"
        
        # Create metadata URL (you'll need to upload to IPFS)
        nft_url = f"ipfs://QmYourCIDHere/unit_{medicine_id}_{unit_serial}.json#arc3"
        
        params = sp()
        txn = tx.AssetCreateTxn(
            sender=self.creator_addr, sp=params,
            total=1, decimals=0, default_frozen=False,
            unit_name=unit_name, asset_name=asset_name,
            url=nft_url,
            manager=self.creator_addr, reserve=self.creator_addr,
            freeze=self.creator_addr, clawback=self.creator_addr
        )
        
        stx = txn.sign(self.creator_sk)
        txid = ALGOD.send_transaction(stx)
        res = wait(txid)
        
        unit_nft_id = res["asset-index"]
        print(f"Unit NFT created: {unit_nft_id}")
        
        return unit_nft_id
    
    def add_medicine(self, medicine_name, batch_no, total_units=1000, expiry_date="2027-08"):
        """Add a new medicine with batch ASA and track it"""
        medicine_id = self.generate_medicine_id(medicine_name, batch_no)
        
        # Create batch ASA
        batch_asa_id = self.create_batch_asa(medicine_name, batch_no, total_units, expiry_date)
        
        # Initialize medicine entry
        if "medicines" not in self.artifacts:
            self.artifacts["medicines"] = {}
        
        self.artifacts["medicines"][medicine_id] = {
            "medicine_name": medicine_name,
            "batch_no": batch_no,
            "batch_asa_id": batch_asa_id,
            "total_units": total_units,
            "expiry_date": expiry_date,
            "created_date": datetime.now().isoformat(),
            "unit_nfts": {}  # Will store individual unit NFT IDs
        }
        
        self.save_artifacts()
        print(f"Medicine {medicine_name} added successfully!")
        print(f"Medicine ID: {medicine_id}")
        print(f"Batch ASA ID: {batch_asa_id}")
        
        return medicine_id, batch_asa_id
    
    def create_unit_nft_for_medicine(self, medicine_id, unit_serial):
        """Create a unit NFT for an existing medicine"""
        if medicine_id not in self.artifacts["medicines"]:
            raise ValueError(f"Medicine {medicine_id} not found")
        
        medicine = self.artifacts["medicines"][medicine_id]
        medicine_name = medicine["medicine_name"]
        batch_no = medicine["batch_no"]
        
        # Create unit NFT
        unit_nft_id = self.create_unit_nft(medicine_name, batch_no, unit_serial)
        
        # Store unit NFT ID
        self.artifacts["medicines"][medicine_id]["unit_nfts"][unit_serial] = unit_nft_id
        
        self.save_artifacts()
        print(f"Unit NFT created for {medicine_name} Unit {unit_serial}: {unit_nft_id}")
        
        return unit_nft_id
    
    def list_medicines(self):
        """List all medicines"""
        if not self.artifacts.get("medicines"):
            print("No medicines found")
            return
        
        print("\n=== MEDICINES INVENTORY ===")
        for medicine_id, medicine in self.artifacts["medicines"].items():
            print(f"\nMedicine ID: {medicine_id}")
            print(f"Name: {medicine['medicine_name']}")
            print(f"Batch: {medicine['batch_no']}")
            print(f"Batch ASA ID: {medicine['batch_asa_id']}")
            print(f"Total Units: {medicine['total_units']}")
            print(f"Expiry: {medicine['expiry_date']}")
            print(f"Unit NFTs: {len(medicine['unit_nfts'])} created")
    
    def get_medicine_info(self, medicine_id):
        """Get detailed info about a specific medicine"""
        if medicine_id not in self.artifacts["medicines"]:
            print(f"Medicine {medicine_id} not found")
            return None
        
        medicine = self.artifacts["medicines"][medicine_id]
        print(f"\n=== {medicine['medicine_name']} DETAILS ===")
        print(f"Medicine ID: {medicine_id}")
        print(f"Batch Number: {medicine['batch_no']}")
        print(f"Batch ASA ID: {medicine['batch_asa_id']}")
        print(f"Total Units: {medicine['total_units']}")
        print(f"Expiry Date: {medicine['expiry_date']}")
        print(f"Created: {medicine['created_date']}")
        
        if medicine['unit_nfts']:
            print(f"\nUnit NFTs:")
            for unit_serial, nft_id in medicine['unit_nfts'].items():
                print(f"  Unit {unit_serial}: {nft_id}")
        
        return medicine

def main():
    manager = MedicineManager()
    
    # Example usage
    print("=== PHARMATRUST MEDICINE MANAGER ===")
    
    # Add a new medicine
    medicine_id, batch_asa_id = manager.add_medicine(
        medicine_name="Amoxy 500",
        batch_no="B2025-09-16",
        total_units=1000,
        expiry_date="2027-08"
    )
    
    # Create some unit NFTs
    manager.create_unit_nft_for_medicine(medicine_id, "U001")
    manager.create_unit_nft_for_medicine(medicine_id, "U002")
    
    # List all medicines
    manager.list_medicines()
    
    # Show detailed info
    manager.get_medicine_info(medicine_id)

if __name__ == "__main__":
    main()
