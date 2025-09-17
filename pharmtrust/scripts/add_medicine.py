#!/usr/bin/env python3
"""
Simple script to add new medicines to the PharmaTrust system
Usage: python add_medicine.py "Medicine Name" "Batch Number" [total_units] [expiry_date]
"""

import sys
from medicine_manager import MedicineManager

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_medicine.py \"Medicine Name\" \"Batch Number\" [total_units] [expiry_date]")
        print("Example: python add_medicine.py \"Amoxy 500\" \"B2025-09-16\" 1000 \"2027-08\"")
        return
    
    medicine_name = sys.argv[1]
    batch_no = sys.argv[2]
    total_units = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    expiry_date = sys.argv[4] if len(sys.argv) > 4 else "2027-08"
    
    print(f"Adding medicine: {medicine_name}")
    print(f"Batch: {batch_no}")
    print(f"Total Units: {total_units}")
    print(f"Expiry: {expiry_date}")
    print("-" * 50)
    
    manager = MedicineManager()
    
    try:
        medicine_id, batch_asa_id = manager.add_medicine(
            medicine_name=medicine_name,
            batch_no=batch_no,
            total_units=total_units,
            expiry_date=expiry_date
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"Medicine ID: {medicine_id}")
        print(f"Batch ASA ID: {batch_asa_id}")
        print(f"Check artifacts.json for updated records")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
