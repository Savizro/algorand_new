#!/usr/bin/env python3
"""
Simple script to add new medicines to the PharmaTrust system
Usage: python add_medicine.py "Medicine Name" "Batch Number" [total_units] [expiry_date]
"""

import sys
from medicine_manager import MedicineManager
import requests
import json

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
LLAMA_MODEL = "llama-4-vision-8b-8192"

def trace_transaction_with_llama(transaction_data):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a blockchain transaction analyst. Trace the following transaction and fetch all real-time related data."
            },
            {
                "role": "user",
                "content": f"Transaction data: {json.dumps(transaction_data)}"
            }
        ],
        "max_tokens": 512
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print("Groq API error:", response.text)
        return None

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
        
        # Example transaction data to send to Llama 4
        transaction_data = {
            "medicine_id": medicine_id,
            "batch_asa_id": batch_asa_id,
            "batch_no": batch_no,
            "total_units": total_units,
            "expiry_date": expiry_date
        }
        llama_response = trace_transaction_with_llama(transaction_data)
        if llama_response:
            print("\nLlama 4 Maverick Vision Model Response:")
            print(llama_response)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
