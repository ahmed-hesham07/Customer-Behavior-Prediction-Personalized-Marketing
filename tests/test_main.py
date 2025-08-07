"""
Unit tests for the Customer Behavior Prediction system.
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from src.data.processor import DataProcessor
from src.models.predictor import CustomerBehaviorPredictor
from src.marketing.email_campaigns import EmailCampaignManager, EmailTemplate

class TestDataProcessor(unittest.TestCase):
    """Test cases for DataProcessor class."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample test data
        self.test_data = pd.DataFrame({
            'Member_number': [1000, 1000, 1001, 1001],
            'name': ['Alice', 'Alice', 'Bob', 'Bob'],
            'Date': ['15-03-2015', '25-03-2015', '16-03-2015', '26-03-2015'],
            'item': ['milk', 'bread', 'milk', 'eggs'],
            'email': ['hekan87089@aravites.com', 'alice@test.com', 'bob@test.com', 'bob@test.com'],
            'Unnamed: 5': [np.nan, np.nan, np.nan, np.nan],
            'Unnamed: 6': [np.nan, np.nan, np.nan, np.nan]
        })
        
        # Save test data to temporary file
        self.test_file = 'test_data.xlsx'
        self.test_data.to_excel(self.test_file, index=False)
        
        self.processor = DataProcessor(self.test_file)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_load_data(self):
        """Test data loading functionality."""
        df = self.processor.load_data()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 4)
        self.assertEqual(df['Member_number'].nunique(), 2)
    
    def test_clean_data(self):
        """Test data cleaning functionality."""
        self.processor.load_data()
        cleaned_df = self.processor.clean_data()
        
        # Check if unnamed columns are removed
        self.assertNotIn('Unnamed: 5', cleaned_df.columns)
        self.assertNotIn('Unnamed: 6', cleaned_df.columns)
        
        # Check if date features are created
        self.assertIn('day_of_month', cleaned_df.columns)
        self.assertIn('month', cleaned_df.columns)
        self.assertIn('year', cleaned_df.columns)
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        self.processor.load_data()
        self.processor.clean_data()
        summary = self.processor.get_data_summary()
        
        self.assertEqual(summary['total_records'], 4)
        self.assertEqual(summary['unique_customers'], 2)
        self.assertEqual(summary['unique_items'], 3)

class TestEmailTemplate(unittest.TestCase):
    """Test cases for EmailTemplate class."""
    
    def test_discount_template(self):
        """Test discount email template generation."""
        template = EmailTemplate.discount_template("John", "milk", 20, "2024-12-31")
        
        self.assertIn("John", template)
        self.assertIn("20%", template)
        self.assertIn("milk", template)
        self.assertIn("2024-12-31", template)
    
    def test_voucher_template(self):
        """Test voucher email template generation."""
        template = EmailTemplate.voucher_template("Jane", 100, "2024-12-31")
        
        self.assertIn("Jane", template)
        self.assertIn("$100", template)
        self.assertIn("2024-12-31", template)
    
    def test_product_recommendation_template(self):
        """Test product recommendation template generation."""
        products = ["milk", "bread", "eggs"]
        template = EmailTemplate.product_recommendation_template("Bob", products)
        
        self.assertIn("Bob", template)
        for product in products:
            self.assertIn(product, template)

class TestCustomerBehaviorPredictor(unittest.TestCase):
    """Test cases for CustomerBehaviorPredictor class."""
    
    def setUp(self):
        """Set up test data."""
        # Create more comprehensive test data
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'Member_number': np.random.randint(1000, 1010, 100),
            'item': np.random.choice(['milk', 'bread', 'eggs', 'cheese'], 100),
            'day_of_month': np.random.randint(1, 31, 100),
            'month': np.random.randint(1, 13, 100),
            'day_of_week': np.random.randint(0, 7, 100),
            'total_purchases': np.random.randint(1, 50, 100),
            'unique_items': np.random.randint(1, 10, 100),
            'tenure_days': np.random.randint(1, 365, 100),
            'purchase_frequency': np.random.uniform(0.1, 2.0, 100),
            'item_frequency': np.random.randint(1, 100, 100),
            'customer_item_count': np.random.randint(1, 10, 100),
            'is_weekend': np.random.choice([0, 1], 100),
            'season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], 100)
        })
        
        self.predictor = CustomerBehaviorPredictor()
    
    def test_prepare_features(self):
        """Test feature preparation."""
        X, y = self.predictor.prepare_features(self.test_data)
        
        self.assertIsNotNone(X)
        self.assertIsNotNone(y)
        self.assertEqual(len(X), len(self.test_data))
        self.assertEqual(len(y), len(self.test_data))

class TestEmailCampaignManager(unittest.TestCase):
    """Test cases for EmailCampaignManager class."""
    
    def setUp(self):
        """Set up test campaign manager."""
        self.campaign_manager = EmailCampaignManager()
    
    def test_email_stats_initialization(self):
        """Test email statistics initialization."""
        stats = self.campaign_manager.email_stats
        
        self.assertEqual(stats['total_sent'], 0)
        self.assertEqual(stats['discounts_sent'], 0)
        self.assertEqual(stats['vouchers_sent'], 0)
        self.assertEqual(stats['recommendations_sent'], 0)
    
    def test_get_campaign_report(self):
        """Test campaign report generation."""
        report = self.campaign_manager.get_campaign_report()
        
        self.assertIn('summary', report)
        self.assertIn('recent_emails', report)
        self.assertIn('campaigns_by_type', report)

if __name__ == '__main__':
    unittest.main()
