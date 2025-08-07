"""
Email marketing system for personalized customer campaigns.
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from config.settings import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailTemplate:
    """Email template management."""
    
    @staticmethod
    def discount_template(customer_name: str, product: str, discount_percent: int, 
                         valid_until: str) -> str:
        """Create discount email template."""
        return f"""
        Dear {customer_name},
        
        We have an exclusive offer just for you!
        
        🎉 Get {discount_percent}% OFF on {product}!
        
        This special offer is valid until {valid_until}.
        
        Don't miss out on this amazing deal - shop now and save!
        
        Best regards,
        Your Grocery Store Team
        
        ---
        This email was sent because you're a valued customer. 
        If you wish to unsubscribe, please reply with 'UNSUBSCRIBE'.
        """
    
    @staticmethod
    def voucher_template(customer_name: str, voucher_amount: int, valid_until: str) -> str:
        """Create voucher email template."""
        return f"""
        Dear {customer_name},
        
        You've been selected for a special reward!
        
        💰 ${voucher_amount} Shopping Voucher
        
        Use this voucher for your next purchase. Valid until {valid_until}.
        
        We appreciate your loyalty and hope to see you soon!
        
        Best regards,
        Your Grocery Store Team
        
        ---
        This email was sent because you're a valued customer.
        If you wish to unsubscribe, please reply with 'UNSUBSCRIBE'.
        """
    
    @staticmethod
    def product_recommendation_template(customer_name: str, recommended_products: List[str]) -> str:
        """Create product recommendation email template."""
        products_list = "\\n".join([f"• {product}" for product in recommended_products])
        
        return f"""
        Dear {customer_name},
        
        Based on your shopping history, we think you might like these products:
        
        {products_list}
        
        Visit our store to discover these and many more great products!
        
        Best regards,
        Your Grocery Store Team
        
        ---
        This email was sent because you're a valued customer.
        If you wish to unsubscribe, please reply with 'UNSUBSCRIBE'.
        """

class EmailCampaignManager:
    """Manages email marketing campaigns."""
    
    def __init__(self):
        self.sent_emails = []
        self.email_stats = {
            'total_sent': 0,
            'discounts_sent': 0,
            'vouchers_sent': 0,
            'recommendations_sent': 0
        }
    
    def send_email(self, recipient_email: str, subject: str, message: str, 
                   dry_run: bool = True) -> bool:
        """Send email to recipient."""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Email would be sent to: {recipient_email}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Message preview: {message[:100]}...")
                return True
            
            if not config.email.address or not config.email.password:
                logger.warning("Email credentials not configured. Running in dry-run mode.")
                return self.send_email(recipient_email, subject, message, dry_run=True)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config.email.address
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(config.email.host, config.email.port)
            
            if config.email.use_tls:
                server.starttls()  # Enable security
            
            server.login(config.email.address, config.email.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(config.email.address, recipient_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    def create_discount_campaign(self, customers_df: pd.DataFrame, 
                               product_predictions: Dict[str, Any], 
                               dry_run: bool = True) -> Dict[str, int]:
        """Create personalized discount campaigns."""
        campaign_stats = {'high_value': 0, 'regular': 0, 'failed': 0}
        
        for _, customer in customers_df.iterrows():
            try:
                customer_name = customer['name']
                customer_email = customer['email']
                
                # Determine discount based on customer value
                if customer.get('total_purchases', 0) > 10:  # High-value customer
                    discount_percent = int(config.marketing.high_value_discount * 100)
                    campaign_stats['high_value'] += 1
                else:
                    discount_percent = int(config.marketing.regular_discount * 100)
                    campaign_stats['regular'] += 1
                
                # Get recommended product
                recommended_product = customer.get('item', 'selected items')
                
                # Calculate valid until date (7 days from now)
                valid_until = (datetime.now() + timedelta(days=7)).strftime("%B %d, %Y")
                
                # Create email content
                subject = f"{discount_percent}% OFF Special Offer - Just for You!"
                message = EmailTemplate.discount_template(
                    customer_name, recommended_product, discount_percent, valid_until
                )
                
                # Send email
                success = self.send_email(customer_email, subject, message, dry_run)
                
                if success:
                    self.email_stats['discounts_sent'] += 1
                    self.email_stats['total_sent'] += 1
                    
                    # Record sent email
                    self.sent_emails.append({
                        'timestamp': datetime.now(),
                        'customer_email': customer_email,
                        'campaign_type': 'discount',
                        'discount_percent': discount_percent,
                        'product': recommended_product
                    })
                
            except Exception as e:
                logger.error(f"Failed to create discount campaign for {customer_email}: {str(e)}")
                campaign_stats['failed'] += 1
        
        return campaign_stats
    
    def create_voucher_campaign(self, low_engagement_customers: pd.DataFrame, 
                              dry_run: bool = True) -> int:
        """Create voucher campaigns for low-engagement customers."""
        vouchers_sent = 0
        
        for _, customer in low_engagement_customers.iterrows():
            try:
                customer_name = customer['name']
                customer_email = customer['email']
                
                # Calculate valid until date (30 days from now)
                valid_until = (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")
                
                # Create email content
                subject = f"Special ${config.marketing.voucher_amount} Voucher - We Miss You!"
                message = EmailTemplate.voucher_template(
                    customer_name, config.marketing.voucher_amount, valid_until
                )
                
                # Send email
                success = self.send_email(customer_email, subject, message, dry_run)
                
                if success:
                    vouchers_sent += 1
                    self.email_stats['vouchers_sent'] += 1
                    self.email_stats['total_sent'] += 1
                    
                    # Record sent email
                    self.sent_emails.append({
                        'timestamp': datetime.now(),
                        'customer_email': customer_email,
                        'campaign_type': 'voucher',
                        'voucher_amount': config.marketing.voucher_amount
                    })
                
            except Exception as e:
                logger.error(f"Failed to create voucher campaign for {customer_email}: {str(e)}")
        
        return vouchers_sent
    
    def create_recommendation_campaign(self, customers_with_recommendations: List[Dict], 
                                     dry_run: bool = True) -> int:
        """Create product recommendation campaigns."""
        recommendations_sent = 0
        
        for customer_data in customers_with_recommendations:
            try:
                customer_name = customer_data['name']
                customer_email = customer_data['email']
                recommended_products = customer_data['recommendations']
                
                if not recommended_products:
                    continue
                
                # Create email content
                subject = "Products You Might Love - Personalized Just for You!"
                message = EmailTemplate.product_recommendation_template(
                    customer_name, recommended_products
                )
                
                # Send email
                success = self.send_email(customer_email, subject, message, dry_run)
                
                if success:
                    recommendations_sent += 1
                    self.email_stats['recommendations_sent'] += 1
                    self.email_stats['total_sent'] += 1
                    
                    # Record sent email
                    self.sent_emails.append({
                        'timestamp': datetime.now(),
                        'customer_email': customer_email,
                        'campaign_type': 'recommendations',
                        'products': recommended_products
                    })
                
            except Exception as e:
                logger.error(f"Failed to create recommendation campaign for {customer_email}: {str(e)}")
        
        return recommendations_sent
    
    def get_campaign_report(self) -> Dict[str, Any]:
        """Generate campaign performance report."""
        return {
            'summary': self.email_stats,
            'recent_emails': self.sent_emails[-10:],  # Last 10 emails
            'campaigns_by_type': {
                'discount': len([e for e in self.sent_emails if e['campaign_type'] == 'discount']),
                'voucher': len([e for e in self.sent_emails if e['campaign_type'] == 'voucher']),
                'recommendations': len([e for e in self.sent_emails if e['campaign_type'] == 'recommendations'])
            }
        }
    
    def export_campaign_data(self, filepath: str):
        """Export campaign data to CSV."""
        df = pd.DataFrame(self.sent_emails)
        df.to_csv(filepath, index=False)
        logger.info(f"Campaign data exported to {filepath}")
