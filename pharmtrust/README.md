# PharmaTrust - Medicine Management System

A blockchain-based pharmaceutical product management system built on Algorand.

## 🚀 Quick Start

### Option 1: Use the Start Script (Recommended)
```bash
cd pharmtrust
python start_server.py
```
This will automatically open your browser to `http://localhost:5000`

### Option 2: Manual Start
```bash
cd pharmtrust
python app.py
```
Then open your browser to `http://localhost:5000`

## 🌐 Web Interface

### Main Dashboard (`http://localhost:5000`)
- Create new medicine batches
- View medicine inventory
- Generate unit NFTs with QR codes
- Real-time balance display

### Product Verification (`http://localhost:5000/verify`)
- Verify product authenticity
- Scan QR codes
- Manual Unit NFT ID entry
- Blockchain verification

## 🔧 API Endpoints

- `GET /api/medicines` - List all medicines
- `POST /api/medicines` - Create new medicine batch
- `POST /api/medicines/{id}/units` - Create unit NFT
- `GET /api/verify/{unit_nft_id}` - Verify product
- `GET /api/balance` - Get account balance
- `GET /api/qr/{unit_nft_id}` - Generate QR code

## 📱 Features

✅ **Medicine Management**
- Create medicine batches with unique Batch ASA IDs
- Generate individual unit NFTs
- Automatic ID generation and storage

✅ **QR Code Generation**
- Real-time QR code creation
- Links to verification page
- Base64 encoded images

✅ **Product Verification**
- Blockchain-based authenticity verification
- QR code scanning interface
- Detailed product information

✅ **Real-time Updates**
- Live inventory refresh
- Instant transaction feedback
- Error handling and validation

## 🛠️ Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   - Make sure you're in the `pharmtrust` directory
   - Run: `pip install -r requirements.txt`

2. **Frontend not loading**
   - Access `http://localhost:5000` (not 5500)
   - Make sure Flask server is running

3. **API errors**
   - Check Flask server is running on port 5000
   - Verify account has sufficient ALGO balance

4. **Import errors**
   - All packages should be installed automatically
   - If issues persist, reinstall: `pip install Flask Flask-CORS qrcode Pillow requests`

## 📊 Current Status

- ✅ Flask server running successfully
- ✅ API endpoints working
- ✅ Medicine inventory: 3 medicines
- ✅ Account balance: ~5.5 ALGO
- ✅ All functionality integrated

## 🔗 Important URLs

- **Main App**: http://localhost:5000
- **Verification**: http://localhost:5000/verify
- **API Test**: Run `python test_api.py`

---

**Note**: Make sure to access the application through the Flask server (port 5000) for proper frontend-backend integration!
