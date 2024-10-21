import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


SHOPIFY_STORE = ""
SHOPIFY_ACCESS_TOKEN = ""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
CLIENT_EMAILS = ["", ""]


def get_shopify_inventory():
    url = (
        f"https://{SHOPIFY_STORE}.myshopify.com/"
        "admin/api/2023-10/products.json"
    )

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(
            f"Failed to fetch inventory from Shopify. "
            f"Status Code: {response.status_code}"
        )
        print(f"Response: {response.text}")
        return None

    products = response.json().get("products", [])
    data = []

    for product in products:
        for variant in product["variants"]:
            data.append({
                "Product": product["title"],
                "Variant": variant["title"],
                "SKU": variant["sku"],
                "Price": variant["price"],
                "Inventory Quantity": variant["inventory_quantity"]
            })

    return pd.DataFrame(data)


def send_inventory_email(dataframe):
    filename = f"Inventory_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    dataframe.to_excel(filename, index=False)

    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = ", ".join(CLIENT_EMAILS)
    message["Subject"] = "Doggles Monthly Inventory Report"

    body = ("Hello! Please find attached the latest Doggles monthly inventory "
            "report.\n\nThis is an automated email; please do not reply.\n\n"
            "For questions or orders, email info@doggles.com or call/text " 
            "(530) 344-1645.\n\n")
    
    message.attach(MIMEText(body, "plain"))

    with open(filename, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        message.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        server.sendmail(EMAIL_SENDER, CLIENT_EMAILS, message.as_string())

        server.quit()
        print("Emails sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    inventory_data = get_shopify_inventory()
    if inventory_data is not None:
        send_inventory_email(inventory_data)


if __name__ == "__main__":
    main()