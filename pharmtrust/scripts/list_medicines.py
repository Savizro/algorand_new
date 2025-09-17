#!/usr/bin/env python3
"""
Script to list all medicines in the PharmaTrust system
"""

from medicine_manager import MedicineManager

def main():
    manager = MedicineManager()
    manager.list_medicines()

if __name__ == "__main__":
    main()
