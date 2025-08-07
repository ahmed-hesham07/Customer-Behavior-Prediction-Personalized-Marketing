"""
Enhanced Customer Behavior Prediction and Personalized Marketing System
"""
import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

from src.data.processor import DataProcessor
from src.models.predictor import CustomerBehaviorPredictor, ProductRecommendationEngine
from src.marketing.email_campaigns import EmailCampaignManager
from src.visualization.dashboard import CustomerAnalyticsDashboard
from config.settings import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('customer_behavior_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CustomerBehaviorAnalysisSystem:
    """Main system orchestrating all components."""
    
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.data_processor = None
        self.predictor = None
        self.recommendation_engine = None
        self.campaign_manager = None
        self.dashboard = None
        
        # Results storage
        self.processed_data = None
        self.rfm_analysis = None
        self.predictions = None
        self.campaign_results = None
        
    def initialize_components(self):
        """Initialize all system components."""
        logger.info("Initializing Customer Behavior Analysis System...")
        
        # Validate configuration
        if not config.validate():
            logger.warning("Configuration validation failed. Some features may not work.")
        
        # Initialize components
        self.data_processor = DataProcessor(self.data_file_path)
        self.predictor = CustomerBehaviorPredictor()
        self.recommendation_engine = ProductRecommendationEngine()
        self.campaign_manager = EmailCampaignManager()
        
        logger.info("All components initialized successfully.")
    
    def run_data_analysis(self):
        """Execute comprehensive data analysis."""
        logger.info("Starting data analysis pipeline...")
        
        # Load and clean data
        raw_data = self.data_processor.load_data()
        logger.info(f"Loaded {len(raw_data)} records from {self.data_file_path}")
        
        # Clean and process data
        self.processed_data = self.data_processor.clean_data()
        self.processed_data = self.data_processor.create_features()
        
        # Get data summary
        summary = self.data_processor.get_data_summary()
        logger.info(f"Data summary: {summary['total_records']} records, "
                   f"{summary['unique_customers']} customers, "
                   f"{summary['unique_items']} unique items")
        
        # Perform RFM analysis
        self.rfm_analysis = self.data_processor.get_customer_segments()
        logger.info(f"Customer segmentation completed. Segments: {self.rfm_analysis['Segment'].value_counts().to_dict()}")
        
        # Initialize dashboard with processed data
        self.dashboard = CustomerAnalyticsDashboard(self.processed_data)
        
        return summary
    
    def run_predictive_modeling(self):
        """Execute predictive modeling pipeline."""
        logger.info("Starting predictive modeling...")
        
        if self.processed_data is None:
            raise ValueError("Data not processed. Run data analysis first.")
        
        # Prepare features and train models
        X, y = self.predictor.prepare_features(self.processed_data)
        model_results = self.predictor.train_models(X, y)
        
        # Generate predictions and recommendations
        self.predictions = self.predictor.get_customer_recommendations(self.processed_data)
        
        # Build product recommendation system
        self.recommendation_engine.build_recommendation_matrix(self.processed_data)
        
        # Add product recommendations to customer data
        for customer in self.predictions['customer_segments']:
            customer_id = customer['Member_number']
            recommendations = self.recommendation_engine.get_product_recommendations(customer_id)
            customer['product_recommendations'] = recommendations
        
        logger.info(f"Predictive modeling completed. Best model: {self.predictor.best_model_name}")
        
        return model_results
    
    def run_marketing_campaigns(self, dry_run: bool = True):
        """Execute marketing campaigns."""
        logger.info(f"Starting marketing campaigns (dry_run={dry_run})...")
        
        if self.predictions is None:
            raise ValueError("Predictions not available. Run predictive modeling first.")
        
        # Create customer dataframes for campaigns
        all_customers = pd.DataFrame(self.predictions['customer_segments'])
        
        # Identify different customer segments for targeted campaigns
        high_value_customers = all_customers[all_customers['purchase_count'] > 10]
        low_engagement_customers = all_customers[all_customers['purchase_count'] <= 3]
        
        # Create discount campaigns
        discount_results = self.campaign_manager.create_discount_campaign(
            high_value_customers, self.predictions, dry_run
        )
        
        # Create voucher campaigns for low-engagement customers
        voucher_results = self.campaign_manager.create_voucher_campaign(
            low_engagement_customers.head(10), dry_run  # Limit to 10 for demo
        )
        
        # Create recommendation campaigns
        customers_with_recs = [
            {
                'name': customer['name'],
                'email': customer['email'],
                'recommendations': customer.get('product_recommendations', [])
            }
            for customer in self.predictions['customer_segments']
            if customer.get('product_recommendations')
        ]
        
        recommendation_results = self.campaign_manager.create_recommendation_campaign(
            customers_with_recs[:20], dry_run  # Limit to 20 for demo
        )
        
        # Generate campaign report
        self.campaign_results = self.campaign_manager.get_campaign_report()
        
        logger.info(f"Marketing campaigns completed. "
                   f"Discounts: {discount_results}, "
                   f"Vouchers: {voucher_results}, "
                   f"Recommendations: {recommendation_results}")
        
        return {
            'discount_results': discount_results,
            'voucher_results': voucher_results,
            'recommendation_results': recommendation_results
        }
    
    def generate_visualizations(self):
        """Generate all visualizations and reports."""
        logger.info("Generating visualizations and reports...")
        
        if self.dashboard is None:
            raise ValueError("Dashboard not initialized. Run data analysis first.")
        
        # Create overview visualizations
        overview = self.dashboard.create_customer_overview()
        
        # Create segmentation visualizations
        self.dashboard.create_customer_segmentation_viz(self.rfm_analysis)
        
        # Create predictive insights
        if self.predictions:
            self.dashboard.create_predictive_insights_viz(self.predictions)
        
        # Create marketing performance visualizations
        if self.campaign_results:
            self.dashboard.create_marketing_performance_viz(self.campaign_results)
        
        # Generate interactive dashboard
        dashboard_file = self.dashboard.create_interactive_dashboard()
        
        # Generate executive summary
        executive_summary = self.dashboard.generate_executive_summary(
            overview, self.rfm_analysis, self.predictions, self.campaign_results
        )
        
        logger.info("All visualizations and reports generated successfully.")
        
        return {
            'overview': overview,
            'dashboard_file': dashboard_file,
            'executive_summary': executive_summary
        }
    
    def save_results(self):
        """Save all results and models."""
        logger.info("Saving results and models...")
        
        # Save processed data
        if self.processed_data is not None:
            self.processed_data.to_csv('processed_customer_data.csv', index=False)
        
        # Save RFM analysis
        if self.rfm_analysis is not None:
            self.rfm_analysis.to_csv('customer_segmentation_rfm.csv', index=False)
        
        # Save predictions
        if self.predictions is not None:
            pd.DataFrame(self.predictions['customer_segments']).to_csv('customer_predictions.csv', index=False)
        
        # Save model
        if self.predictor is not None:
            self.predictor.save_model('customer_behavior_model.joblib')
        
        # Save campaign data
        if self.campaign_manager is not None:
            self.campaign_manager.export_campaign_data('campaign_results.csv')
        
        logger.info("All results saved successfully.")
    
    def run_complete_analysis(self, dry_run: bool = True):
        """Run the complete analysis pipeline."""
        try:
            logger.info("=" * 60)
            logger.info("STARTING COMPLETE CUSTOMER BEHAVIOR ANALYSIS")
            logger.info("=" * 60)
            
            # Initialize system
            self.initialize_components()
            
            # Run data analysis
            data_summary = self.run_data_analysis()
            
            # Run predictive modeling
            model_results = self.run_predictive_modeling()
            
            # Run marketing campaigns
            campaign_results = self.run_marketing_campaigns(dry_run)
            
            # Generate visualizations
            viz_results = self.generate_visualizations()
            
            # Save all results
            self.save_results()
            
            logger.info("=" * 60)
            logger.info("ANALYSIS COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
            # Print summary
            print("\\n" + "=" * 60)
            print("CUSTOMER BEHAVIOR ANALYSIS - EXECUTION SUMMARY")
            print("=" * 60)
            print(f"✅ Data processed: {data_summary['total_records']} records")
            print(f"✅ Customers analyzed: {data_summary['unique_customers']}")
            print(f"✅ Predictive model trained: {self.predictor.best_model_name}")
            print(f"✅ Marketing campaigns created: {campaign_results}")
            print(f"✅ Visualizations generated: {len([f for f in viz_results.keys() if f != 'executive_summary'])}")
            print(f"✅ Interactive dashboard: {viz_results['dashboard_file']}")
            print("\\n📊 Check the generated files for detailed analysis:")
            print("   - customer_overview.png")
            print("   - customer_segmentation.png") 
            print("   - predictive_insights.png")
            print("   - marketing_performance.png")
            print("   - interactive_dashboard.html")
            print("   - executive_summary.md")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise

def main():
    """Main application entry point."""
    print("🚀 Enhanced Customer Behavior Prediction & Personalized Marketing System")
    print("=" * 70)
    
    # Configuration
    data_file = 'Groceries_dataset2.xlsx'
    
    if not os.path.exists(data_file):
        print(f"❌ Error: Data file '{data_file}' not found!")
        print("Please ensure the Excel file is in the project directory.")
        return
    
    # Initialize and run system
    system = CustomerBehaviorAnalysisSystem(data_file)
    
    try:
        # Run complete analysis
        system.run_complete_analysis(dry_run=False)  # Set to False to actually send emails
        
    except Exception as e:
        print(f"❌ System error: {str(e)}")
        logger.error(f"System error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
