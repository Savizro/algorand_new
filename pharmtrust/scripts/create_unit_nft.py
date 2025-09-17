#!/usr/bin/env python3
"""
Script to create unit NFTs for existing medicines
Usage: python create_unit_nft.py "Medicine ID" "Unit Serial"
"""

import sys
from medicine_manager import MedicineManager

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_unit_nft.py \"Medicine ID\" \"Unit Serial\"")
        print("Example: python create_unit_nft.py \"Amoxy_500_B2025-09-16_20241216\" \"U001\"")
        print("\nTo see available medicines, run: python list_medicines.py")
        return
    
    medicine_id = sys.argv[1]
    unit_serial = sys.argv[2]
    
    print(f"Creating unit NFT for Medicine: {medicine_id}")
    print(f"Unit Serial: {unit_serial}")
    print("-" * 50)
    
    manager = MedicineManager()
    
    try:
        unit_nft_id = manager.create_unit_nft_for_medicine(medicine_id, unit_serial)
        
        print(f"\n✅ SUCCESS!")
        print(f"Unit NFT ID: {unit_nft_id}")
        print(f"Check artifacts.json for updated records")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()