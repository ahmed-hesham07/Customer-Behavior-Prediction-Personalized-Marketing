# Customer-Behavior-Prediction-Personalized-Marketing

This Python script utilizes machine learning techniques, particularly Random Forest Classifier, to predict customer shopping patterns based on historical data. It imports data from an Excel spreadsheet, preprocesses it by converting text labels to numerical values, and then splits it into training and testing sets. The trained model is then used to predict future purchases.

The script further generates personalized discount notifications for customers based on their predicted shopping preferences. Discounts include a 5% offer on the most predicted product category and a 20% discount on the least predicted product categories. Additionally, it creates personalized vouchers for selected customers. The system sends out these notifications and vouchers via email using SMTP, ensuring timely and targeted communication with customers.
