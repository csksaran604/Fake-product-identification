"""
app.py - Main Flask Application Controller

Features:
- Product verification by QR/manual Product ID
- 1000 automatically generated sample products
- Unique QR code for every product
- SQLite database
- Educational blockchain integrity verification
"""

import os
import re
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

import qrcode

import database as db
from blockchain import Blockchain


# ============================================================
# APPLICATION SETUP
# ============================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "anti_fake_product_blockchain_secret_2026"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QR_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "generated_codes"
)

os.makedirs(QR_FOLDER, exist_ok=True)


# Educational blockchain
blockchain = Blockchain(difficulty=2)


# ============================================================
# ADMIN LOGIN DECORATOR
# ============================================================

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):

            flash(
                "Administrator login required to access this page.",
                "warning"
            )

            return redirect(
                url_for(
                    "login",
                    next=request.url
                )
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# QR CODE GENERATOR
# ============================================================

def generate_qr_code(
    verification_code: str,
    product_id: str
) -> str:

    os.makedirs(QR_FOLDER, exist_ok=True)

    clean_code = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        verification_code.strip()
    )

    filename = f"qr_{clean_code}.png"

    filepath = os.path.join(
        QR_FOLDER,
        filename
    )

    qr = qrcode.QRCode(

        version=1,

        error_correction=
        qrcode.constants.ERROR_CORRECT_H,

        box_size=10,

        border=3,
    )

    qr.add_data(
        verification_code.strip().upper()
    )

    qr.make(
        fit=True
    )

    img = qr.make_image(

        fill_color="#0f172a",

        back_color="#ffffff"
    )

    img.save(filepath)

    return f"generated_codes/{filename}"


# ============================================================
# INPUT CODE EXTRACTOR
# ============================================================

def extract_code_from_input(user_input: str) -> str:

    val = user_input.strip()

    if not val:
        return ""

    # QR might contain a URL
    if "code=" in val:

        match = re.search(
            r"code=([^&]+)",
            val
        )

        if match:

            return match.group(1).strip()

    return val


# ============================================================
# CREATE INITIAL SAMPLE PRODUCTS
# ============================================================

def seed_sample_data():

    existing_products = db.get_all_products()

    # Blockchain must contain genesis block
    if not blockchain.chain:
        blockchain.create_genesis_block()

    # If database already contains products,
    # load/rebuild blockchain
    if existing_products:

        loaded = db.load_blockchain_from_db(
            blockchain
        )

        if not loaded:

            blockchain.chain = []

            blockchain.create_genesis_block()

            for p in reversed(existing_products):

                product_data = {

                    "product_id":
                    p["product_id"],

                    "name":
                    p["name"],

                    "manufacturer":
                    p["manufacturer"],

                    "category":
                    p["category"],

                    "batch_number":
                    p["batch_number"],

                    "verification_code":
                    p["verification_code"],
                }

                blockchain.add_block(
                    p["product_id"],
                    product_data
                )

            db.save_all_blocks_to_db(
                blockchain
            )

        return

    # Database empty
    # Add a few starter products

    starter_products = [

        {

            "name":
            "Smart Wireless Headphones",

            "product_id":
            "START1001",

            "manufacturer":
            "ABC Electronics",

            "category":
            "Electronics",

            "batch_number":
            "START-BATCH-001",

            "mfg_date":
            "2026-01-15",

            "exp_date":
            "",

            "description":
            "Starter sample product.",

            "verification_code":
            "AUTH-START-1001-XYZ",
        },

        {

            "name":
            "Organic Olive Oil",

            "product_id":
            "START1002",

            "manufacturer":
            "Mediterranean Groves",

            "category":
            "Food & Beverage",

            "batch_number":
            "START-BATCH-002",

            "mfg_date":
            "2026-02-10",

            "exp_date":
            "2028-02-10",

            "description":
            "Starter sample food product.",

            "verification_code":
            "AUTH-START-1002-MED",
        },

    ]

    for product in starter_products:

        qr_path = generate_qr_code(

            product["verification_code"],

            product["product_id"]
        )

        product["qr_code_path"] = qr_path

        success, message = db.add_product(
            product
        )

        if success:

            blockchain_data = {

                "product_id":
                product["product_id"],

                "name":
                product["name"],

                "manufacturer":
                product["manufacturer"],

                "category":
                product["category"],

                "batch_number":
                product["batch_number"],

                "verification_code":
                product["verification_code"],
            }

            blockchain.add_block(

                product["product_id"],

                blockchain_data
            )

    db.save_all_blocks_to_db(
        blockchain
    )


# ============================================================
# BULK ADD 1000 PRODUCTS + QR CODES
# ============================================================

def bulk_add_1000_products():

    categories = [

        "Electronics",

        "Food & Beverage",

        "Cosmetics",

        "Apparel",

        "Home Appliances",

        "Personal Care",

        "Sports",

        "Books",

        "Toys",

        "Accessories",
    ]


    manufacturers = [

        "Alpha Industries",

        "Beta Products",

        "Gamma Manufacturing",

        "Delta Enterprises",

        "Omega Corporation",

        "Nova Industries",

        "Prime Products",

        "Vertex Manufacturing",

        "Global Goods",

        "Future Tech",
    ]


    product_names = [

        "Wireless Headphones",

        "Organic Food Product",

        "Skin Care Product",

        "Running Shoes",

        "Electric Appliance",

        "Personal Care Item",

        "Sports Equipment",

        "Premium Book",

        "Educational Toy",

        "Fashion Accessory",
    ]


    existing_ids = set()


    all_existing_products = db.get_all_products()


    for product in all_existing_products:

        existing_ids.add(

            product["product_id"]
        )


    added_count = 0


    for i in range(1, 1001):

        product_id = f"PROD{i:04d}"


        # Already registered
        if product_id in existing_ids:

            continue


        index = (

            i - 1

        ) % len(categories)


        verification_code = (

            f"AUTH-PROD-{i:04d}-VERIFY"

        )


        # Create QR image

        qr_path = generate_qr_code(

            verification_code,

            product_id
        )


        product = {

            "name":
            f"{product_names[index]} {i}",


            "product_id":
            product_id,


            "manufacturer":
            manufacturers[index],


            "category":
            categories[index],


            "batch_number":
            f"BATCH-2026-{i:04d}",


            "mfg_date":
            "2026-01-15",


            "exp_date":
            "2028-01-15",


            "description":
            (
                f"Automatically generated "
                f"sample product number {i} "
                f"for the verification system."
            ),


            "verification_code":
            verification_code,


            "qr_code_path":
            qr_path,
        }


        # Add to SQLite database

        success, message = db.add_product(

            product
        )


        if success:

            blockchain_data = {

                "product_id":
                product_id,


                "name":
                product["name"],


                "manufacturer":
                product["manufacturer"],


                "category":
                product["category"],


                "batch_number":
                product["batch_number"],


                "verification_code":
                verification_code,
            }


            blockchain.add_block(

                product_id,

                blockchain_data
            )


            added_count += 1


    # Save all blockchain blocks

    db.save_all_blocks_to_db(

        blockchain
    )


    print("=" * 60)

    print(

        f"SUCCESS: {added_count} products added."

    )

    print(

        "QR codes generated in static/generated_codes/"

    )

    print("=" * 60)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

db.init_db()

db.seed_default_admin()

seed_sample_data()

bulk_add_1000_products()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    metrics = db.get_dashboard_metrics()

    sample_products = db.get_all_products()[:4]

    return render_template(

        "index.html",

        metrics=metrics,

        samples=sample_products
    )


# ============================================================
# VERIFY PAGE
# ============================================================

@app.route("/verify")
def verify():

    prefill_code = request.args.get(

        "code",

        ""
    ).strip()


    sample_products = db.get_all_products()[:10]


    return render_template(

        "verify.html",

        prefill_code=prefill_code,

        sample_products=sample_products,
    )


# ============================================================
# PRODUCT VERIFICATION
# ============================================================

@app.route(
    "/verify/check",

    methods=["GET", "POST"]
)
def verify_check():

    raw_query = ""


    if request.method == "POST":

        raw_query = request.form.get(

            "query",

            ""
        ).strip()


    else:

        raw_query = request.args.get(

            "query",

            ""
        ).strip()


    search_val = extract_code_from_input(

        raw_query
    )


    if not search_val:

        flash(

            "Please provide a Product ID or verification code.",

            "warning"
        )


        return redirect(

            url_for("verify")
        )


    client_ip = (

        request.remote_addr

        or

        "127.0.0.1"
    )


    # Search SQLite

    product_row = db.get_product_by_id_or_code(

        search_val
    )


    # ========================================================
    # PRODUCT NOT FOUND
    # ========================================================

    if not product_row:

        db.log_verification(

            search_val,

            None,

            "PRODUCT_NOT_FOUND",

            client_ip
        )


        return render_template(

            "result.html",

            status="NOT_VERIFIED",

            query=search_val,

            message=(
                "This product code is not registered "
                "in the system."
            ),

            product=None,

            block=None,
        )


    product_dict = dict(

        product_row
    )


    verification_payload = {

        "product_id":
        product_dict["product_id"],


        "name":
        product_dict["name"],


        "manufacturer":
        product_dict["manufacturer"],


        "category":
        product_dict["category"],


        "batch_number":
        product_dict["batch_number"],


        "verification_code":
        product_dict["verification_code"],
    }


    # ========================================================
    # BLOCKCHAIN VERIFICATION
    # ========================================================

    status, msg, block_data = (

        blockchain.verify_product_record(

            product_dict["product_id"],

            verification_payload
        )
    )


    # ========================================================
    # VERIFIED
    # ========================================================

    if status == "VERIFIED":

        db.log_verification(

            product_dict["verification_code"],

            product_dict["product_id"],

            "VERIFIED",

            client_ip
        )


        return render_template(

            "result.html",

            status="VERIFIED",

            query=search_val,

            message=(
                "Product record verified successfully."
            ),

            product=product_dict,

            block=block_data,
        )


    # ========================================================
    # INTEGRITY FAILED
    # ========================================================

    db.log_verification(

        product_dict["verification_code"],

        product_dict["product_id"],

        "INTEGRITY_FAILED",

        client_ip
    )


    return render_template(

        "result.html",

        status="INTEGRITY_FAILED",

        query=search_val,

        message=msg,

        product=product_dict,

        block=block_data,
    )


# ============================================================
# QR DOWNLOAD
# ============================================================

@app.route(
    "/download-qr/<path:filename>"
)
def download_qr(filename):

    return send_from_directory(

        QR_FOLDER,

        filename,

        as_attachment=True
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(

    "/login",

    methods=["GET", "POST"]
)
def login():

    if session.get(

        "admin_logged_in"
    ):

        return redirect(

            url_for("dashboard")
        )


    if request.method == "POST":

        username = request.form.get(

            "username",

            ""
        ).strip()


        password = request.form.get(

            "password",

            ""
        ).strip()


        if db.verify_admin_login(

            username,

            password
        ):

            session["admin_logged_in"] = True

            session["admin_username"] = username


            flash(

                "Welcome back, Administrator!",

                "success"
            )


            next_page = request.args.get(

                "next"
            )


            return redirect(

                next_page

                or

                url_for("dashboard")
            )


        flash(

            "Invalid administrator credentials.",

            "danger"
        )


    return render_template(

        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()


    flash(

        "You have been signed out successfully.",

        "info"
    )


    return redirect(

        url_for("login")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/dashboard")
@admin_required
def dashboard():

    metrics = db.get_dashboard_metrics()

    recent_logs = db.get_recent_logs(

        limit=15
    )

    recent_products = db.get_all_products()[:10]


    chain_valid, chain_msg, broken_idx = (

        blockchain.validate_chain()
    )


    return render_template(

        "dashboard.html",

        metrics=metrics,

        recent_logs=recent_logs,

        recent_products=recent_products,

        blockchain_chain=blockchain.chain,

        chain_valid=chain_valid,

        chain_msg=chain_msg,

        broken_idx=broken_idx,
    )


# ============================================================
# REGISTER PRODUCT
# ============================================================

@app.route(

    "/register",

    methods=["GET", "POST"]
)
@admin_required
def register_product():

    if request.method == "POST":

        name = request.form.get(

            "name",

            ""
        ).strip()


        product_id = request.form.get(

            "product_id",

            ""
        ).strip().upper()


        manufacturer = request.form.get(

            "manufacturer",

            ""
        ).strip()


        category = request.form.get(

            "category",

            ""
        ).strip()


        batch_number = request.form.get(

            "batch_number",

            ""
        ).strip().upper()


        mfg_date = request.form.get(

            "mfg_date",

            ""
        ).strip()


        exp_date = request.form.get(

            "exp_date",

            ""
        ).strip()


        description = request.form.get(

            "description",

            ""
        ).strip()


        verification_code = request.form.get(

            "verification_code",

            ""
        ).strip().upper()


        if not all([

            name,

            product_id,

            manufacturer,

            category,

            batch_number,

            mfg_date,

            verification_code
        ]):

            flash(

                "Please fill in all required fields.",

                "danger"
            )


            return render_template(

                "register_product.html"
            )


        if db.get_product_by_id(

            product_id
        ):

            flash(

                f"Product ID '{product_id}' already exists.",

                "danger"
            )


            return render_template(

                "register_product.html"
            )


        if db.get_product_by_code(

            verification_code
        ):

            flash(

                "Verification code already exists.",

                "danger"
            )


            return render_template(

                "register_product.html"
            )


        qr_rel_path = generate_qr_code(

            verification_code,

            product_id
        )


        product_record = {

            "name":
            name,


            "product_id":
            product_id,


            "manufacturer":
            manufacturer,


            "category":
            category,


            "batch_number":
            batch_number,


            "mfg_date":
            mfg_date,


            "exp_date":
            exp_date,


            "description":
            description,


            "verification_code":
            verification_code,


            "qr_code_path":
            qr_rel_path,
        }


        success, db_msg = db.add_product(

            product_record
        )


        if not success:

            flash(

                db_msg,

                "danger"
            )


            return render_template(

                "register_product.html"
            )


        blockchain_data = {

            "product_id":
            product_id,


            "name":
            name,


            "manufacturer":
            manufacturer,


            "category":
            category,


            "batch_number":
            batch_number,


            "verification_code":
            verification_code,
        }


        new_block = blockchain.add_block(

            product_id,

            blockchain_data
        )


        db.save_all_blocks_to_db(

            blockchain
        )


        flash(

            f"Product '{name}' successfully registered!",

            "success"
        )


        return render_template(

            "register_product.html",

            registered=product_record,

            block=new_block.to_dict(),
        )


    return render_template(

        "register_product.html"
    )


# ============================================================
# PRODUCTS PAGE
# ============================================================

@app.route("/products")
@admin_required
def products():

    search = request.args.get(

        "search",

        ""
    ).strip()


    category = request.args.get(

        "category",

        ""
    ).strip()


    all_products = db.get_all_products(

        search=search if search else None,

        category=category if category else None
    )


    categories = db.get_categories()


    return render_template(

        "products.html",

        products=all_products,

        categories=categories,

        selected_search=search,

        selected_category=category,
    )


# ============================================================
# DELETE PRODUCT
# ============================================================

@app.route(

    "/products/delete/<product_id>",

    methods=["POST"]
)
@admin_required
def delete_product(product_id):

    success, msg = db.delete_product(

        product_id
    )


    if success:

        flash(

            msg,

            "info"
        )


    else:

        flash(

            msg,

            "danger"
        )


    return redirect(

        url_for("products")
    )


# ============================================================
# TAMPER DEMO
# ============================================================

@app.route(

    "/api/tamper-demo",

    methods=["POST"]
)
@admin_required
def tamper_demo():

    data = request.get_json() or {}


    product_id = data.get(

        "product_id",

        "PROD0001"
    )


    success, msg = blockchain.tamper_block_for_demo(

        product_id
    )


    if success:

        db.save_all_blocks_to_db(

            blockchain
        )


        return jsonify({

            "success": True,

            "message": msg
        })


    return jsonify({

        "success": False,

        "message": msg

    }), 400


# ============================================================
# REPAIR BLOCKCHAIN
# ============================================================

@app.route(

    "/api/repair-chain",

    methods=["POST"]
)
@admin_required
def repair_chain():

    success, msg = blockchain.repair_chain()


    if success:

        db.save_all_blocks_to_db(

            blockchain
        )


        return jsonify({

            "success": True,

            "message": msg
        })


    return jsonify({

        "success": False,

        "message": msg

    }), 400


# ============================================================
# DASHBOARD DATA API
# ============================================================

@app.route("/api/dashboard-data")
@admin_required
def dashboard_data():

    metrics = db.get_dashboard_metrics()


    return jsonify(

        metrics
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print("=" * 65)

    print(
        " FAKE PRODUCT IDENTIFICATION SYSTEM"
    )

    print(
        " 1000 SAMPLE PRODUCTS + QR CODES"
    )

    print(
        " Running: http://127.0.0.1:5000"
    )

    print(
        " Admin: admin / admin123"
    )

    print("=" * 65)


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )