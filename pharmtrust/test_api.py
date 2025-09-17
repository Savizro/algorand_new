#!/usr/bin/env python3
"""
Test script for the PharmaTrust API
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing PharmaTrust API...")
    
    # Test 1: Get medicines
    print("\n1. Testing GET /api/medicines")
    try:
        response = requests.get(f"{base_url}/api/medicines")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('medicines', {}))} medicines")
            for medicine_id, medicine in data.get('medicines', {}).items():
                print(f"   - {medicine['medicine_name']} (Batch: {medicine['batch_no']})")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return
    
    # Test 2: Get balance
    print("\n2. Testing GET /api/balance")
    try:
        response = requests.get(f"{base_url}/api/balance")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Balance = {data.get('balance', 0)} ALGO")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Create a test medicine
    print("\n3. Testing POST /api/medicines")
    test_medicine = {
        "medicine_name": "Test Medicine",
        "batch_no": "TEST001",
        "total_units": 100,
        "expiry_date": "2025-12"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/medicines",
            headers={"Content-Type": "application/json"},
            json=test_medicine
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Created medicine with Batch ASA ID: {data.get('batch_asa_id')}")
            medicine_id = data.get('medicine_id')
            
            # Test 4: Create unit NFT
            print("\n4. Testing POST /api/medicines/{id}/units")
            unit_data = {"unit_serial": "TEST001"}
            response = requests.post(
                f"{base_url}/api/medicines/{medicine_id}/units",
                headers={"Content-Type": "application/json"},
                json=unit_data
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: Created Unit NFT ID: {data.get('unit_nft_id')}")
                unit_nft_id = data.get('unit_nft_id')
                
                # Test 5: Verify product
                print("\n5. Testing GET /api/verify/{unit_nft_id}")
                response = requests.get(f"{base_url}/api/verify/{unit_nft_id}")
                if response.status_code == 200:
                    data = response.json()
                    verification = data.get('verification', {})
                    print(f"✅ Success: Verified {verification.get('medicine_name')} - {verification.get('unit_serial')}")
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    test_api()
