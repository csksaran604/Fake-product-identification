# Identifying Fake Products Through a Barcode-Based Blockchain System

> **Academic College Project Prototype**  
> **Department of Computer Science & Engineering**  
> **Topic:** Anti-Counterfeiting, Cryptographic Verification & Supply Chain Integrity  

---

## 1. Project Overview & Abstract

Counterfeit goods pose severe threats to consumer safety, public health, and brand reputation across industries such as pharmaceuticals, luxury goods, electronics, and packaged foods. Traditional centralized databases are susceptible to single-point-of-failure vulnerabilities, insider tampering, and unauthorized record alterations.

This project, **"Identifying Fake Products Through a Barcode-Based Blockchain System"**, is a modern, responsive web-based prototype designed to demonstrate how physical packaging identifiers (QR codes and barcodes) can be cryptographically anchored to a transparent, tamper-evident **SHA-256 Blockchain Ledger**.

### Important Academic Disclaimer
> [!IMPORTANT]
> This system is an **educational software prototype**. The software proves that an identification code was legitimately registered on an immutable ledger. However, in the real world, a printed barcode or QR code alone **cannot physically guarantee** that an item is genuine, because printed labels can be duplicated without physical cryptographic security tags (such as tamper-evident NFC tags, holographic seals, or PUF microchips).

---

## 2. Key Features

1. **Consumer Verification Portal (`/verify`)**:
   - **Dual-Mode Verification**:
     - **Live Camera Scanner**: Scans QR codes using the device camera via `html5-qrcode`.
     - **Image File Upload**: Drag-and-drop or select an image file to decode the QR code.
     - **Manual Code Input**: Search by Product ID (e.g. `PROD1001`) or Verification Code (e.g. `AUTH-PROD-1001-XYZ`).
   - **1-Click Presentation Demo Pills**: Quickly test authentic and counterfeit codes with a single click.

2. **Distinct Verification Result States (`/verify/check`)**:
   - ✅ **PRODUCT VERIFIED**: Displayed when the item exists in the database and its cryptographic fingerprint matches the blockchain block. Shows complete product specifications, manufacturer details, and blockchain block receipts.
   - ⚠️ **PRODUCT NOT VERIFIED**: Displayed when the scanned code does not exist in the registered database.
   - ⚠️ **RECORD INTEGRITY CHECK FAILED**: Displayed when database information has been maliciously altered, causing SHA-256 hash validation against the blockchain block to fail.

3. **Manufacturer & Admin Portal (`/login`, `/register`, `/products`)**:
   - **Session-Based Authentication**: Secure admin login using hashed passwords (`pbkdf2:sha256`).
   - **Product Registration**: Captures Product Name, Product ID, Manufacturer, Category, Batch Number, Manufacturing Date, Expiry Date, and Description.
   - **Automatic QR Code Generation**: Creates high-contrast PNG QR codes stored in `static/generated_codes/`.
   - **Instant Download**: Download generated QR code images for packaging printing.
   - **Product Catalog**: Live search, category filtering, QR code preview thumbnails, and product deletion.

4. **Educational Blockchain Engine (`blockchain.py`)**:
   - Pure Python implementation with SHA-256 cryptographic hashing.
   - Genesis block initialization (`index: 0`, `previous_hash: 000...000`).
   - Proof-of-Work (PoW) consensus simulation (difficulty = 2 leading zeros).
   - Global chain validation (`validate_chain()`).
   - Block data fingerprint verification (`compute_data_hash()`).
   - SQLite persistence (`blockchain_blocks` table) so ledger data survives server restarts.

5. **Interactive Tamper & Repair Demonstration Tool**:
   - Admin dashboard includes a **"Simulate Attack (Tamper Block)"** button.
   - Intentionally corrupts a block's metadata to demonstrate to evaluators/professors how blockchain cryptographic pointers detect unauthorized changes immediately.
   - **"Re-mine & Repair Ledger"** button recalculates and restores the chain to a clean state.

6. **Admin Dashboard & Analytics (`/dashboard`)**:
   - KPI metric cards (Total Products, Authentic Scans, Suspicious Scans, Mined Blocks).
   - Horizontal visual blockchain explorer showing connected block nodes.
   - Real-time Chart.js interactive graphs (Category breakdown doughnut chart and scan outcome bar chart).
   - Verification audit log table recording every customer scan attempt.

---

## 3. System Architecture & Workflow

```
+-------------------------------------------------------------------------+
|                            USER INTERFACES                              |
|   Consumer Scanner (/verify)        |      Admin Management (/dashboard)|
|   - Live Camera QR Scanner          |      - Product Registration Form  |
|   - QR Image Upload Decoder         |      - Product Management Catalog |
|   - Manual Code Entry               |      - Tamper Simulation Engine   |
+-------------------------------------+-----------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------------+
|                      FLASK BACKEND ENGINE (app.py)                      |
|   - REST Routing & Session Auth     |      - QR Code Generator (Pillow) |
|   - Verification Logic Orchestrator |      - Flash Alert Messaging      |
+---------------------------------+---------------------------------------+
                                  |
            +---------------------+---------------------+
            v                                           v
+-----------------------+                   +-----------------------+
|  DATABASE (database.py) |                 |  LEDGER (blockchain.py)|
|  - SQLite (products.db) |                 |  - SHA-256 Hashing    |
|  - admins               |                 |  - Proof-of-Work Nonce |
|  - products             |                 |  - Genesis & Blocks   |
|  - verification_logs    |                 |  - Cryptographic Chain|
|  - blockchain_blocks    |                 |  - Tamper Detection   |
+-----------------------+                   +-----------------------+
```

---

## 4. Technology Stack

- **Backend Framework**: Python Flask (3.1.x)
- **Database**: SQLite 3 (Built-in Python `sqlite3` with parameterized SQL)
- **Blockchain Simulation**: Python `hashlib` (SHA-256) & `json`
- **QR Code Generation**: `qrcode[pil]` & `Pillow`
- **Frontend Architecture**: HTML5, Vanilla CSS3 (Dark Glassmorphic Theme), JavaScript (ES6)
- **QR Scanner Engine**: `html5-qrcode` (HTML5 Camera API & Canvas decoder)
- **Data Visualization**: `Chart.js`
- **Iconography & Fonts**: FontAwesome 6, Google Fonts (*Outfit*, *Inter*, *JetBrains Mono*)

---

## 5. Directory Structure

```
fake_product_detector/
│
├── app.py                     # Main Flask application, routes, and controllers
├── blockchain.py              # Educational SHA-256 blockchain simulation engine
├── database.py                # SQLite database queries, schema, and persistence
├── test_app.py                # Automated unittest suite for all routes & flows
├── requirements.txt           # Python package dependencies
├── README.md                  # Comprehensive documentation and project guide
│
├── templates/                 # Jinja2 HTML5 Templates
│   ├── base.html              # Responsive layout, navigation, and disclaimer banner
│   ├── index.html             # Landing page, workflow steps, benefits, stats
│   ├── login.html             # Administrator authentication form
│   ├── register_product.html  # Product registration & QR download view
│   ├── products.html          # Product catalog with search and category filters
│   ├── verify.html            # Customer verification portal (Camera + Manual)
│   ├── result.html            # Verification outcomes (Verified, Unknown, Tampered)
│   └── dashboard.html         # Admin KPI analytics, chain explorer, tamper panel
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom dark glassmorphism design system
│   ├── js/
│   │   └── script.js          # QR scanner, Chart.js, sample fill, and tamper triggers
│   └── generated_codes/       # Storage directory for auto-generated QR images
│
└── database/
    └── products.db            # SQLite relational database file
```

---

## 6. Installation & Setup Instructions

### Prerequisites
- Python 3.9 or newer installed (e.g. Python 3.10, 3.11, 3.12, 3.14).
- `pip` (Python Package Installer).

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "c:\projects\Fack Product"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
*Required packages:*
- `Flask>=3.0.0`
- `qrcode[pil]>=8.0`
- `Pillow>=10.0.0`
- `Werkzeug>=3.0.0`

### Step 3: Run the Application
Execute the main application controller:
```bash
python app.py
```
Or run using Flask CLI:
```bash
flask run --port=5000
```

The application will start on:
```
http://127.0.0.1:5000
```

---

## 7. Demo Administrator Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` |

*Passwords are securely stored as cryptographic hashes (`pbkdf2:sha256`) in SQLite.*

---

## 8. Pre-Seeded Sample Products for Presentation

When the system boots for the first time, it automatically initializes the Genesis Block and seeds 4 realistic sample products across diverse categories:

| Product Name | Product ID | Category | Batch Number | Verification Code |
| :--- | :--- | :--- | :--- | :--- |
| **Smart Wireless Headphones** | `PROD1001` | Electronics | `BATCH2026A` | `AUTH-PROD-1001-XYZ` |
| **Pure Life Organic Olive Oil** | `PROD1002` | Food & Beverage | `BATCH-OLV-99` | `AUTH-PROD-1002-MED` |
| **VitaBoost Vitamin C Serum** | `PROD1003` | Pharmaceuticals | `BATCH-VD-441` | `AUTH-PROD-1003-DER` |
| **AeroSpeed Pro Running Shoes** | `PROD1004` | Apparel | `BATCH-ASP-88` | `AUTH-PROD-1004-RUN` |

---

## 9. How to Demonstrate the Project (Step-by-Step Viva Guide)

### Step 1: Customer Product Verification
1. Navigate to `http://127.0.0.1:5000/verify`.
2. **Test Authentic Product**:
   - Click the quick-sample pill: `Smart Wireless Headphones (PROD1001)`.
   - The code `AUTH-PROD-1001-XYZ` is entered automatically.
   - Click **Verify Against Blockchain Ledger**.
   - Result: Shows the green **✅ PRODUCT VERIFIED** card, product specifications, and Block #1 receipt.
3. **Test Counterfeit / Unregistered Product**:
   - Click the pill: `Test Counterfeit Code`.
   - Result: Shows the red **⚠️ PRODUCT NOT VERIFIED** card indicating an unregistered product.

### Step 2: Administrator Login & Dashboard
1. Click **Admin Login** in the navigation bar.
2. Enter `admin` / `admin123`.
3. View the **Dashboard**:
   - Real-time KPI counters (Registered products, verified scans, total blocks).
   - Category distribution doughnut chart and scan outcome bar chart.
   - Visual blockchain flow showing blocks connected by cryptographic hash pointers.

### Step 3: Live Tampering & Security Attack Simulation
1. In the Admin Dashboard, locate the **Blockchain Ledger Cryptographic Health** card.
2. Click **"Simulate Attack (Tamper Block)"**.
3. The server intentionally alters the block metadata of `PROD1001` without re-mining.
4. The ledger health immediately turns red: **COMPROMISED AT BLOCK #1**.
5. Go back to `/verify` and test `PROD1001` again.
6. Result: Shows the warning **⚠️ RECORD INTEGRITY CHECK FAILED**.
   > *"The stored verification record does not match the blockchain record. Further verification is required."*
7. Return to Dashboard and click **"Re-mine & Repair Ledger"** to restore cryptographic consistency.

### Step 4: Register a New Product & Generate QR Code
1. Click **Register Product** in the admin navigation.
2. Fill in product details (or click **Auto-Generate** for the verification code).
3. Click **Register & Mine Block**.
4. A new block is mined with proof-of-work, and a new QR code is generated.
5. Click **Download QR Image** to save the packaging code.

---

## 10. Running Automated Tests

A comprehensive unit test suite is included in `test_app.py`. To run all automated tests:

```bash
python test_app.py
```

Expected output:
```
......
----------------------------------------------------------------------
Ran 6 tests in 0.740s

OK
```

---

## 11. Technical Viva Questions & Answers (For Students)

**Q1: What problem does blockchain solve in fake product detection?**  
*Answer:* In a standard database, a malicious insider or hacker can quietly change batch numbers, expiry dates, or genuine serial numbers. In a blockchain, each block's cryptographic hash depends on its contents and the previous block's hash. Any modification breaks the chain pointers, making unauthorized alterations immediately detectable.

**Q2: Why does the project use Proof-of-Work (PoW)?**  
*Answer:* PoW prevents denial-of-service and unauthorized block rewriting by requiring computational effort (finding a `nonce` that produces a hash starting with target leading zeros, e.g., `00`).

**Q3: Can a barcode or QR code alone stop counterfeiters?**  
*Answer:* No. A physical printed QR code can be photographed and printed onto fake packaging. To achieve end-to-end security in production industry deployments, blockchain verification must be paired with physical anti-tamper measures, such as encrypted NFC chips with dynamic rolling authentication keys, holographic tags, or tamper-evident seals.

---

## 12. Limitations & Future Enhancements

### Limitations of Current Prototype
- Simulated single-node blockchain running in Python rather than a multi-node distributed peer-to-peer network (e.g. Hyperledger Fabric or Ethereum).
- Physical QR codes are static and can be duplicated by physical cloning.

### Future Enhancements
- **Decentralized Network Integration**: Deploy smart contracts on Ethereum / Polygon testnets or Hyperledger Fabric.
- **Dynamic NFC / RFID Integration**: Replace static QR codes with cryptographic NFC chips that generate one-time authentication tokens (rolling OTPs) upon physical tap.
- **Geographic Anomaly Detection**: Log GPS/IP coordinates of verification scans to trigger automatic alerts if the same unique code is scanned simultaneously in two different cities.

---

## 13. License & Academic Attribution
Developed as an educational engineering prototype for academic demonstration purposes. Free to use, adapt, and build upon for collegiate study and research.
