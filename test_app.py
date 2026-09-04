"""
test_app.py - Automated Verification and Route Testing Suite
"""

import unittest
from app import app
import database as db
from blockchain import Blockchain

class TestFakeProductSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage(self):
        """Test landing page loads cleanly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Identifying Fake Products", response.data)
        self.assertIn(b"Verify a Product Now", response.data)

    def test_verify_page(self):
        """Test customer verification page."""
        response = self.app.get('/verify')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Verify Product Authenticity", response.data)
        self.assertIn(b"Live Camera Scanner", response.data)

    def test_verify_authentic_product(self):
        """Test verifying an authentic registered sample product."""
        response = self.app.get('/verify/check?query=AUTH-PROD-1001-XYZ')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PRODUCT VERIFIED", response.data)
        self.assertIn(b"Smart Wireless Headphones", response.data)
        self.assertIn(b"AUTHENTICALLY REGISTERED", response.data)

    def test_verify_unregistered_fake_code(self):
        """Test verifying an unregistered / counterfeit code."""
        response = self.app.get('/verify/check?query=FAKE-NONEXISTENT-CODE-999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PRODUCT NOT VERIFIED", response.data)
        self.assertIn(b"not registered in the system", response.data)

    def test_admin_login_and_dashboard(self):
        """Test admin authentication flow."""
        # Check login page
        resp = self.app.get('/login')
        self.assertEqual(resp.status_code, 200)

        # Attempt invalid login
        resp_bad = self.app.post('/login', data={'username': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn(b"Invalid administrator credentials", resp_bad.data)

        # Login with valid credentials
        resp_good = self.app.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(resp_good.status_code, 200)
        self.assertIn(b"System Analytics", resp_good.data)

        # Access protected dashboard
        resp_dash = self.app.get('/dashboard')
        self.assertEqual(resp_dash.status_code, 200)
        self.assertIn(b"Total Registered Products", resp_dash.data)

        # Test products catalog
        resp_prod = self.app.get('/products')
        self.assertEqual(resp_prod.status_code, 200)
        self.assertIn(b"Product Catalog", resp_prod.data)

    def test_blockchain_integrity_and_tamper_demo(self):
        """Test blockchain tamper detection simulation."""
        from app import blockchain
        valid, _, _ = blockchain.validate_chain()
        self.assertTrue(valid)

        # 2. Tamper block for PROD1001
        success, _ = blockchain.tamper_block_for_demo("PROD1001")
        self.assertTrue(success)

        # 3. Validating chain should now return False
        tampered_valid, _, _ = blockchain.validate_chain()
        self.assertFalse(tampered_valid)

        # 4. Verification of PROD1001 should show INTEGRITY_FAILED
        resp = self.app.get('/verify/check?query=PROD1001')
        self.assertIn(b"RECORD INTEGRITY CHECK FAILED", resp.data)

        # 5. Repair chain
        repaired, _ = blockchain.repair_chain()
        self.assertTrue(repaired)
        db.save_all_blocks_to_db(blockchain)
        restored_valid, _, _ = blockchain.validate_chain()
        self.assertTrue(restored_valid)

if __name__ == '__main__':
    unittest.main()
