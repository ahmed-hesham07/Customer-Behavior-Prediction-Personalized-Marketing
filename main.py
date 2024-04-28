import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

df = pd.read_excel('Groceries_dataset2.xlsx')

df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
df['day_of_month'] = df['Date'].dt.day

le = LabelEncoder()
df['item'] = le.fit_transform(df['item'])

X = df[['Member_number', 'item']]
y = df['day_of_month']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


score = model.score(X_test, y_test)
print(f'Model accuracy: {score * 100:.2f}%')

predictions = model.predict(X_test)
print(predictions)

most_predicted_product = le.inverse_transform([predictions[0]])[0]
least_predicted_products = ', '.join(le.inverse_transform(predictions[-5:]))

most_predicted_day = pd.Series(predictions).value_counts().idxmax()
least_predicted_day = pd.Series(predictions).value_counts().idxmin()

least_predicted_client = df['name'].iloc[-1]
print(least_predicted_client)

discount_message_most = f"Discount 5% on the {most_predicted_product} on the {least_predicted_day}th of the month."
discount_message_least = f"Discount 20% on these products: {least_predicted_products} on the {most_predicted_day}th of the month."
voucher_message = f"A voucher with $200 is created for {least_predicted_client}, it will expire on {least_predicted_day}th of this month."


def send_email(receiver_email, subject, message):
    sender_email = 'Your E-mail'
    password = 'Your Password'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    server.login(sender_email, password)

    email = MIMEMultipart()
    email['From'] = sender_email
    email['To'] = receiver_email
    email['Subject'] = subject
    email.attach(MIMEText(message, 'plain'))

    server.send_message(email)


customers_sent = set()

for index, row in df.iterrows():
    name = row['name']
    customer_email = row['email']

    if name not in customers_sent:
        personalized_message_most = f"Dear {name}, {discount_message_most}"
        personalized_message_least = f"Dear {name}, {discount_message_least}"

        send_email(customer_email, 'Discount 5% off', personalized_message_most)
        send_email(customer_email, 'Discount 20% off', personalized_message_least)

        customers_sent.add(name)

        if name == least_predicted_client:
            personalized_voucher_message = f"Dear {name}, {voucher_message}"
            send_email(customer_email, 'Voucher', personalized_voucher_message)

    else:
        continue