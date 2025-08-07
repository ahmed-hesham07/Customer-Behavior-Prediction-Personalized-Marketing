"""
Data visualization and analytics dashboard for customer behavior insights.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class CustomerAnalyticsDashboard:
    """Comprehensive analytics dashboard for customer behavior analysis."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.fig_size = (12, 8)
        
    def create_customer_overview(self) -> Dict[str, Any]:
        """Create customer overview visualizations."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Customer Behavior Overview', fontsize=16, fontweight='bold')
        
        # 1. Customer Distribution by Purchase Count
        customer_purchases = self.df['Member_number'].value_counts()
        axes[0, 0].hist(customer_purchases.values, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribution of Customer Purchase Counts')
        axes[0, 0].set_xlabel('Number of Purchases')
        axes[0, 0].set_ylabel('Number of Customers')
        
        # 2. Top 10 Most Popular Items
        top_items = self.df['item'].value_counts().head(10)
        axes[0, 1].barh(range(len(top_items)), top_items.values, color='lightcoral')
        axes[0, 1].set_yticks(range(len(top_items)))
        axes[0, 1].set_yticklabels(top_items.index)
        axes[0, 1].set_title('Top 10 Most Popular Items')
        axes[0, 1].set_xlabel('Purchase Count')
        
        # 3. Purchase Trends by Month
        monthly_purchases = self.df.groupby('month').size()
        axes[1, 0].plot(monthly_purchases.index, monthly_purchases.values, marker='o', linewidth=2, markersize=8)
        axes[1, 0].set_title('Purchase Trends by Month')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Number of Purchases')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Purchase Distribution by Day of Week
        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dow_purchases = self.df['day_of_week'].value_counts().sort_index()
        axes[1, 1].bar(range(len(dow_purchases)), dow_purchases.values, color='lightgreen', alpha=0.8)
        axes[1, 1].set_xticks(range(len(dow_purchases)))
        axes[1, 1].set_xticklabels(dow_names)
        axes[1, 1].set_title('Purchases by Day of Week')
        axes[1, 1].set_xlabel('Day of Week')
        axes[1, 1].set_ylabel('Number of Purchases')
        
        plt.tight_layout()
        plt.savefig('customer_overview.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return {
            'total_customers': self.df['Member_number'].nunique(),
            'total_purchases': len(self.df),
            'avg_purchases_per_customer': len(self.df) / self.df['Member_number'].nunique(),
            'top_items': top_items.to_dict(),
            'peak_month': monthly_purchases.idxmax(),
            'peak_day': dow_names[dow_purchases.idxmax()]
        }
    
    def create_customer_segmentation_viz(self, rfm_data: pd.DataFrame):
        """Create customer segmentation visualizations."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Customer Segmentation Analysis (RFM)', fontsize=16, fontweight='bold')
        
        # 1. RFM Scores Distribution
        axes[0, 0].hist(rfm_data['Recency'], bins=20, alpha=0.7, label='Recency', color='red')
        axes[0, 0].set_title('Recency Distribution')
        axes[0, 0].set_xlabel('Days Since Last Purchase')
        axes[0, 0].set_ylabel('Number of Customers')
        
        # 2. Frequency vs Monetary
        axes[0, 1].scatter(rfm_data['Frequency'], rfm_data['Monetary'], alpha=0.6, color='blue')
        axes[0, 1].set_title('Frequency vs Monetary Value')
        axes[0, 1].set_xlabel('Purchase Frequency')
        axes[0, 1].set_ylabel('Monetary Value (Item Variety)')
        
        # 3. Customer Segments Distribution
        segment_counts = rfm_data['Segment'].value_counts()
        axes[1, 0].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', startangle=90)
        axes[1, 0].set_title('Customer Segments Distribution')
        
        # 4. RFM Heatmap
        rfm_summary = rfm_data.groupby('Segment')[['Recency', 'Frequency', 'Monetary']].mean()
        im = axes[1, 1].imshow(rfm_summary.T, cmap='YlOrRd', aspect='auto')
        axes[1, 1].set_xticks(range(len(rfm_summary.index)))
        axes[1, 1].set_xticklabels(rfm_summary.index, rotation=45)
        axes[1, 1].set_yticks(range(len(rfm_summary.columns)))
        axes[1, 1].set_yticklabels(rfm_summary.columns)
        axes[1, 1].set_title('RFM Metrics by Segment')
        
        # Add colorbar
        plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.savefig('customer_segmentation.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_dashboard(self) -> str:
        """Create interactive dashboard using Plotly."""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Purchase Timeline', 'Item Popularity', 
                          'Customer Purchase Frequency', 'Seasonal Trends',
                          'Day of Month Analysis', 'Customer Loyalty'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Purchase Timeline
        daily_purchases = self.df.groupby('Date').size().reset_index(name='purchases')
        fig.add_trace(
            go.Scatter(x=daily_purchases['Date'], y=daily_purchases['purchases'],
                      mode='lines+markers', name='Daily Purchases'),
            row=1, col=1
        )
        
        # 2. Item Popularity (Top 10)
        top_items = self.df['item'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=top_items.values, y=top_items.index, orientation='h',
                   name='Item Popularity'),
            row=1, col=2
        )
        
        # 3. Customer Purchase Frequency
        customer_freq = self.df['Member_number'].value_counts()
        fig.add_trace(
            go.Histogram(x=customer_freq.values, nbinsx=20, name='Purchase Frequency'),
            row=2, col=1
        )
        
        # 4. Seasonal Trends
        seasonal_data = self.df.groupby('season').size()
        fig.add_trace(
            go.Bar(x=seasonal_data.index, y=seasonal_data.values, name='Seasonal Purchases'),
            row=2, col=2
        )
        
        # 5. Day of Month Analysis
        day_month_data = self.df.groupby('day_of_month').size()
        fig.add_trace(
            go.Scatter(x=day_month_data.index, y=day_month_data.values,
                      mode='lines+markers', name='Day of Month'),
            row=3, col=1
        )
        
        # 6. Customer Loyalty (Purchase Span)
        customer_loyalty = self.df.groupby('Member_number')['Date'].agg(['min', 'max'])
        customer_loyalty['span_days'] = (customer_loyalty['max'] - customer_loyalty['min']).dt.days
        fig.add_trace(
            go.Histogram(x=customer_loyalty['span_days'], nbinsx=20, name='Customer Span'),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="Customer Behavior Analytics Dashboard",
            title_x=0.5,
            height=1200,
            showlegend=False
        )
        
        # Save as HTML
        fig.write_html("interactive_dashboard.html")
        logger.info("Interactive dashboard saved as 'interactive_dashboard.html'")
        
        return "interactive_dashboard.html"
    
    def create_predictive_insights_viz(self, predictions: Dict[str, Any]):
        """Visualize predictive model insights."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Predictive Model Insights', fontsize=16, fontweight='bold')
        
        # 1. Feature Importance
        if 'feature_importance' in predictions['model_performance']:
            importance = predictions['model_performance']['feature_importance']
            if importance:
                features = list(importance.keys())[:10]  # Top 10 features
                importances = [importance[f] for f in features]
                
                axes[0, 0].barh(range(len(features)), importances, color='purple', alpha=0.7)
                axes[0, 0].set_yticks(range(len(features)))
                axes[0, 0].set_yticklabels(features)
                axes[0, 0].set_title('Top 10 Feature Importance')
                axes[0, 0].set_xlabel('Importance Score')
        
        # 2. Prediction Distribution
        day_predictions = predictions['day_predictions']
        days = list(day_predictions.keys())
        counts = list(day_predictions.values())
        
        axes[0, 1].bar(days, counts, color='orange', alpha=0.7)
        axes[0, 1].set_title('Predicted Shopping Days Distribution')
        axes[0, 1].set_xlabel('Day of Month')
        axes[0, 1].set_ylabel('Number of Predictions')
        
        # 3. High Confidence Predictions
        high_conf = predictions['high_confidence_customers']
        if high_conf:
            conf_df = pd.DataFrame(high_conf)
            conf_dist = conf_df['prediction_confidence'].hist(bins=20, ax=axes[1, 0], 
                                                            color='green', alpha=0.7)
            axes[1, 0].set_title('High Confidence Predictions Distribution')
            axes[1, 0].set_xlabel('Prediction Confidence')
            axes[1, 0].set_ylabel('Frequency')
        
        # 4. Customer Segments Summary
        segments = predictions['customer_segments']
        if segments:
            seg_df = pd.DataFrame(segments)
            seg_counts = seg_df['purchase_count'].value_counts().head(10)
            axes[1, 1].bar(range(len(seg_counts)), seg_counts.values, color='teal', alpha=0.7)
            axes[1, 1].set_title('Customer Purchase Count Distribution')
            axes[1, 1].set_xlabel('Purchase Count Range')
            axes[1, 1].set_ylabel('Number of Customers')
        
        plt.tight_layout()
        plt.savefig('predictive_insights.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_marketing_performance_viz(self, campaign_report: Dict[str, Any]):
        """Visualize marketing campaign performance."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Marketing Campaign Performance', fontsize=16, fontweight='bold')
        
        # 1. Campaign Summary
        summary = campaign_report['summary']
        categories = list(summary.keys())
        values = list(summary.values())
        
        axes[0, 0].bar(categories, values, color=['blue', 'green', 'orange', 'red'], alpha=0.7)
        axes[0, 0].set_title('Campaign Summary')
        axes[0, 0].set_ylabel('Count')
        plt.setp(axes[0, 0].xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Campaigns by Type
        campaigns_by_type = campaign_report['campaigns_by_type']
        type_names = list(campaigns_by_type.keys())
        type_counts = list(campaigns_by_type.values())
        
        axes[0, 1].pie(type_counts, labels=type_names, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Campaigns by Type')
        
        # 3. Recent Email Timeline (if available)
        recent_emails = campaign_report.get('recent_emails', [])
        if recent_emails:
            email_df = pd.DataFrame(recent_emails)
            email_df['date'] = pd.to_datetime(email_df['timestamp']).dt.date
            daily_emails = email_df.groupby('date').size()
            
            axes[1, 0].plot(daily_emails.index, daily_emails.values, marker='o', linewidth=2)
            axes[1, 0].set_title('Recent Email Activity')
            axes[1, 0].set_xlabel('Date')
            axes[1, 0].set_ylabel('Emails Sent')
            plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Campaign Type Distribution Over Time
        if recent_emails:
            type_timeline = email_df.groupby(['date', 'campaign_type']).size().unstack(fill_value=0)
            type_timeline.plot(kind='bar', stacked=True, ax=axes[1, 1], alpha=0.8)
            axes[1, 1].set_title('Campaign Types Over Time')
            axes[1, 1].set_xlabel('Date')
            axes[1, 1].set_ylabel('Number of Campaigns')
            plt.setp(axes[1, 1].xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig('marketing_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_executive_summary(self, overview: Dict[str, Any], 
                                 rfm_data: pd.DataFrame,
                                 predictions: Dict[str, Any],
                                 campaign_report: Dict[str, Any]) -> str:
        """Generate executive summary report."""
        summary = f"""
# EXECUTIVE SUMMARY - Customer Behavior Analysis & Marketing Performance

## Key Business Metrics
- **Total Customers**: {overview['total_customers']:,}
- **Total Purchases**: {overview['total_purchases']:,}
- **Average Purchases per Customer**: {overview['avg_purchases_per_customer']:.2f}
- **Peak Shopping Month**: {overview['peak_month']}
- **Peak Shopping Day**: {overview['peak_day']}

## Customer Segmentation Insights
- **Champions**: {len(rfm_data[rfm_data['Segment'] == 'Champions'])} customers
- **Loyal Customers**: {len(rfm_data[rfm_data['Segment'] == 'Loyal Customers'])} customers
- **At Risk**: {len(rfm_data[rfm_data['Segment'] == 'At Risk'])} customers
- **Cannot Lose Them**: {len(rfm_data[rfm_data['Segment'] == 'Cannot Lose Them'])} customers

## Predictive Model Performance
- **Best Model**: {predictions['model_performance']['best_model']}
- **High Confidence Predictions**: {len(predictions['high_confidence_customers'])} customers

## Marketing Campaign Results
- **Total Emails Sent**: {campaign_report['summary']['total_sent']}
- **Discount Campaigns**: {campaign_report['summary']['discounts_sent']}
- **Voucher Campaigns**: {campaign_report['summary']['vouchers_sent']}
- **Recommendation Campaigns**: {campaign_report['summary']['recommendations_sent']}

## Top 5 Most Popular Items
{chr(10).join([f"{i+1}. {item} ({count} purchases)" for i, (item, count) in enumerate(list(overview['top_items'].items())[:5])])}

## Recommendations
1. **Focus on Champions and Loyal Customers**: Increase engagement with high-value segments
2. **Re-engage At-Risk Customers**: Implement targeted voucher campaigns
3. **Optimize Peak Times**: Leverage {overview['peak_month']} and {overview['peak_day']} insights
4. **Expand Popular Items**: Stock more of top-performing products
5. **Personalization**: Continue improving prediction accuracy for better targeting

---
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Save summary to file
        with open('executive_summary.md', 'w') as f:
            f.write(summary)
        
        logger.info("Executive summary saved as 'executive_summary.md'")
        return summary
