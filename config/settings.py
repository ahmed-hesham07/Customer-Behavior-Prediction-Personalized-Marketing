"""
Configuration management for the Customer Behavior Prediction system.
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class EmailConfig:
    """Email configuration settings."""
    host: str
    port: int
    address: str
    password: str
    use_tls: bool

@dataclass
class ModelConfig:
    """Machine learning model configuration."""
    random_state: int
    test_size: float
    n_estimators: int
    
@dataclass
class MarketingConfig:
    """Marketing campaign configuration."""
    high_value_discount: float
    regular_discount: float
    voucher_amount: int

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.email = EmailConfig(
            host=os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
            port=int(os.getenv('EMAIL_PORT', 587)),
            address=os.getenv('EMAIL_ADDRESS', ''),
            password=os.getenv('EMAIL_PASSWORD', ''),
            use_tls=os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
        )
        
        self.model = ModelConfig(
            random_state=int(os.getenv('MODEL_RANDOM_STATE', 42)),
            test_size=float(os.getenv('TEST_SIZE', 0.2)),
            n_estimators=int(os.getenv('N_ESTIMATORS', 100))
        )
        
        self.marketing = MarketingConfig(
            high_value_discount=float(os.getenv('HIGH_VALUE_DISCOUNT', 0.20)),
            regular_discount=float(os.getenv('REGULAR_DISCOUNT', 0.05)),
            voucher_amount=int(os.getenv('VOUCHER_AMOUNT', 200))
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.email.address or not self.email.password:
            print("Warning: Email credentials not configured")
            return False
        return True

# Global configuration instance
config = Config()
