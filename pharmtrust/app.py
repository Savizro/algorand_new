from flask import Flask, request, jsonify, render_template, send_file  # type: ignore
from flask_cors import CORS  # type: ignore
import json
import qrcode  # type: ignore
import io
import base64
from pathlib import Path
import os
from datetime import datetime
import uuid

# Import our medicine manager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from medicine_manager import MedicineManager  # type: ignore

app = Flask(__name__)
CORS(app)

# Initialize medicine manager
medicine_manager = MedicineManager()

# Configuration
ROOT = Path(__file__).resolve().parent
UPLOAD_FOLDER = ROOT / 'static' / 'qr_codes'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_file(f'static/{filename}')

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    """Get all medicines"""
    try:
        medicines = medicine_manager.artifacts.get('medicines', {})
        return jsonify({
            'success': True,
            'medicines': medicines
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medicines', methods=['POST'])
def create_medicine():
    """Create a new medicine with batch ASA"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['medicine_name', 'batch_no']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        medicine_name = data['medicine_name']
        batch_no = data['batch_no']
        total_units = data.get('total_units', 1000)
        expiry_date = data.get('expiry_date', '2027-08')
        
        # Check if medicine already exists
        medicine_id = medicine_manager.generate_medicine_id(medicine_name, batch_no)
        if medicine_id in medicine_manager.artifacts.get('medicines', {}):
            return jsonify({
                'success': False,
                'error': f'Medicine with batch {batch_no} already exists'
            }), 400
        
        # Create the medicine
        medicine_id, batch_asa_id = medicine_manager.add_medicine(
            medicine_name=medicine_name,
            batch_no=batch_no,
            total_units=total_units,
            expiry_date=expiry_date
        )
        
        return jsonify({
            'success': True,
            'medicine_id': medicine_id,
            'batch_asa_id': batch_asa_id,
            'message': f'Medicine {medicine_name} created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medicines/<medicine_id>/units', methods=['POST'])
def create_unit_nft(medicine_id):
    """Create a unit NFT for an existing medicine"""
    try:
        data = request.get_json()
        unit_serial = data.get('unit_serial', f'U{str(uuid.uuid4())[:8]}')
        
        # Create unit NFT
        unit_nft_id = medicine_manager.create_unit_nft_for_medicine(medicine_id, unit_serial)
        
        # Generate QR code
        qr_data = {
            'medicine_id': medicine_id,
            'unit_nft_id': unit_nft_id,
            'unit_serial': unit_serial,
            'timestamp': datetime.now().isoformat()
        }
        
        qr_code_data = json.dumps(qr_data)
        qr_image = generate_qr_code(qr_code_data)
        
        return jsonify({
            'success': True,
            'unit_nft_id': unit_nft_id,
            'unit_serial': unit_serial,
            'qr_code': qr_image,
            'message': f'Unit NFT created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medicines/<medicine_id>', methods=['GET'])
def get_medicine_details(medicine_id):
    """Get detailed information about a specific medicine"""
    try:
        medicine = medicine_manager.get_medicine_info(medicine_id)
        if not medicine:
            return jsonify({
                'success': False,
                'error': 'Medicine not found'
            }), 404
        
        return jsonify({
            'success': True,
            'medicine': medicine_manager.artifacts['medicines'][medicine_id]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/verify/<unit_nft_id>', methods=['GET'])
def verify_product(unit_nft_id):
    """Verify a product using its Unit NFT ID"""
    try:
        # Find the medicine that contains this unit NFT
        medicines = medicine_manager.artifacts.get('medicines', {})
        found_medicine = None
        found_unit_serial = None
        
        for medicine_id, medicine in medicines.items():
            if 'unit_nfts' in medicine:
                for serial, nft_id in medicine['unit_nfts'].items():
                    if str(nft_id) == str(unit_nft_id):
                        found_medicine = medicine
                        found_unit_serial = serial
                        break
        
        if not found_medicine:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        return jsonify({
            'success': True,
            'verification': {
                'medicine_name': found_medicine['medicine_name'],
                'batch_no': found_medicine['batch_no'],
                'unit_serial': found_unit_serial,
                'unit_nft_id': unit_nft_id,
                'expiry_date': found_medicine['expiry_date'],
                'created_date': found_medicine['created_date'],
                'authentic': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/verify/<unit_nft_id>')
def verify_page(unit_nft_id):
    """Product verification page"""
    return render_template('verify.html', unit_nft_id=unit_nft_id)

@app.route('/verify')
def verify_page_no_id():
    """Product verification page without ID"""
    return render_template('verify.html', unit_nft_id='')

@app.route('/api/qr/<unit_nft_id>')
def get_qr_code(unit_nft_id):
    """Generate QR code for a specific Unit NFT ID"""
    try:
        # Create QR code data
        qr_data = {
            'unit_nft_id': unit_nft_id,
            'verification_url': f'/verify/{unit_nft_id}',
            'timestamp': datetime.now().isoformat()
        }
        
        qr_code_data = json.dumps(qr_data)
        qr_image = generate_qr_code(qr_code_data)
        
        return qr_image, 200, {'Content-Type': 'image/png'}
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_qr_code(data):
    """Generate QR code and return as base64 encoded image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return base64.b64encode(img_buffer.getvalue()).decode()

@app.route('/api/balance')
def get_balance():
    """Get account balance"""
    try:
        from check_balance import ALGOD, acct  # type: ignore
        addr, _ = acct("creator")
        balance = ALGOD.account_info(addr)["amount"] / 1e6
        return jsonify({
            'success': True,
            'balance': balance,
            'address': addr
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
