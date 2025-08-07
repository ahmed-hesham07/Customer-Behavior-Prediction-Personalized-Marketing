"""
Data processing and analysis module for customer behavior prediction.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data loading, cleaning, and preprocessing."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.cleaned_df = None
        
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel file."""
        try:
            self.df = pd.read_excel(self.file_path)
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess the data."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Create a copy for cleaning
        self.cleaned_df = self.df.copy()
        
        # Remove unnamed columns
        cols_to_drop = [col for col in self.cleaned_df.columns if 'Unnamed' in str(col)]
        self.cleaned_df = self.cleaned_df.drop(columns=cols_to_drop)
        
        # Convert date column
        self.cleaned_df['Date'] = pd.to_datetime(self.cleaned_df['Date'], format='%d-%m-%Y')
        
        # Extract date features
        self.cleaned_df['day_of_month'] = self.cleaned_df['Date'].dt.day
        self.cleaned_df['month'] = self.cleaned_df['Date'].dt.month
        self.cleaned_df['year'] = self.cleaned_df['Date'].dt.year
        self.cleaned_df['day_of_week'] = self.cleaned_df['Date'].dt.dayofweek
        self.cleaned_df['day_of_year'] = self.cleaned_df['Date'].dt.dayofyear
        
        # Create customer features
        customer_stats = self.cleaned_df.groupby('Member_number').agg({
            'Date': ['count', 'min', 'max'],
            'item': 'nunique'
        }).reset_index()
        
        customer_stats.columns = ['Member_number', 'total_purchases', 'first_purchase', 
                                'last_purchase', 'unique_items']
        
        # Calculate customer tenure and frequency
        customer_stats['tenure_days'] = (customer_stats['last_purchase'] - 
                                       customer_stats['first_purchase']).dt.days
        customer_stats['purchase_frequency'] = (customer_stats['total_purchases'] / 
                                               (customer_stats['tenure_days'] + 1))
        
        # Merge customer features back
        self.cleaned_df = self.cleaned_df.merge(customer_stats, on='Member_number', how='left')
        
        logger.info(f"Data cleaned successfully. Shape: {self.cleaned_df.shape}")
        return self.cleaned_df
    
    def get_data_summary(self) -> Dict:
        """Get comprehensive data summary."""
        if self.cleaned_df is None:
            raise ValueError("Data not cleaned. Call clean_data() first.")
        
        summary = {
            'total_records': len(self.cleaned_df),
            'unique_customers': self.cleaned_df['Member_number'].nunique(),
            'unique_items': self.cleaned_df['item'].nunique(),
            'date_range': {
                'start': self.cleaned_df['Date'].min(),
                'end': self.cleaned_df['Date'].max()
            },
            'top_items': self.cleaned_df['item'].value_counts().head(10).to_dict(),
            'top_customers': self.cleaned_df['Member_number'].value_counts().head(10).to_dict()
        }
        
        return summary
    
    def create_features(self) -> pd.DataFrame:
        """Create additional features for machine learning."""
        if self.cleaned_df is None:
            raise ValueError("Data not cleaned. Call clean_data() first.")
        
        # Item frequency features
        item_freq = self.cleaned_df['item'].value_counts().to_dict()
        self.cleaned_df['item_frequency'] = self.cleaned_df['item'].map(item_freq)
        
        # Customer-item interaction features
        customer_item_counts = self.cleaned_df.groupby(['Member_number', 'item']).size().reset_index(name='customer_item_count')
        self.cleaned_df = self.cleaned_df.merge(customer_item_counts, on=['Member_number', 'item'], how='left')
        
        # Seasonal features
        self.cleaned_df['is_weekend'] = self.cleaned_df['day_of_week'].isin([5, 6]).astype(int)
        self.cleaned_df['season'] = self.cleaned_df['month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        
        return self.cleaned_df
    
    def get_customer_segments(self) -> pd.DataFrame:
        """Segment customers based on purchase behavior."""
        if self.cleaned_df is None:
            raise ValueError("Data not cleaned. Call clean_data() first.")
        
        # RFM Analysis (Recency, Frequency, Monetary - using item count as proxy for monetary)
        current_date = self.cleaned_df['Date'].max()
        
        rfm = self.cleaned_df.groupby('Member_number').agg({
            'Date': lambda x: (current_date - x.max()).days,  # Recency
            'item': ['count', 'nunique']  # Frequency and Monetary
        })
        
        # Flatten column names
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        rfm = rfm.reset_index()
        
        # Create quintiles for each metric
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
        
        # Combine scores
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        
        # Define customer segments
        def segment_customers(rfm_score):
            if rfm_score in ['555', '554', '544', '545', '454', '455', '445']:
                return 'Champions'
            elif rfm_score in ['543', '444', '435', '355', '354', '345', '344', '335']:
                return 'Loyal Customers'
            elif rfm_score in ['512', '511', '422', '421', '412', '411', '311']:
                return 'Potential Loyalists'
            elif rfm_score in ['533', '532', '531', '523', '522', '521', '515', '514', '513', '425', '424', '413', '414', '415', '315', '314', '313']:
                return 'New Customers'
            elif rfm_score in ['155', '154', '144', '214', '215', '115', '114']:
                return 'At Risk'
            elif rfm_score in ['255', '254', '245', '244', '253', '252', '243', '242', '235', '234', '225', '224', '153', '152', '145', '143', '142', '135', '134', '125', '124']:
                return 'Cannot Lose Them'
            else:
                return 'Others'
        
        rfm['Segment'] = rfm['RFM_Score'].apply(segment_customers)
        
        return rfm
