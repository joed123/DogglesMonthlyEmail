import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# Credentials redacted for security

# Shopify API Configuration
SHOPIFY_STORE = ""
SHOPIFY_ACCESS_TOKEN = ""

# Email Server (SMTP) Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""

# Recipient List
CLIENT_EMAILS = ["", ""]


def get_shopify_inventory():
    """
        Fetches product inventory data from the Shopify store API, filters for
        in-stock items, and returns the result as a pandas DataFrame.
        """
    url = (
        f"https://{SHOPIFY_STORE}"
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

    # Iterate through all products and their variants to extract key inventory details
    for product in products:
        for variant in product["variants"]:
            data.append({
                "Product": product["title"],
                "Variant": variant["title"],
                "SKU": variant["sku"],
                "Price": variant["price"],
                "Inventory Quantity": variant["inventory_quantity"]
            })

    df = pd.DataFrame(data)

    # Filter out any products/variants that have zero or negative inventory
    df_filtered = df[df['Inventory Quantity'] > 0]

    df_selected = df_filtered[[
        'Product', 'SKU', 'Variant', 'Inventory Quantity'
        ]]

    df_selected.columns = ['PRODUCT', 'SKU', 'VARIANT', 'QUANTITY']

    return df_selected


def send_inventory_email(dataframe):
    """
        Takes a pandas DataFrame, saves it as both .xlsx and .csv files,
        and emails both files as attachments to the list of recipients.
        """

    # Create time-stamped filenames for the attachments
    xlsx_filename = f"Inventory_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    csv_filename = f"Inventory_{datetime.now().strftime('%Y-%m-%d')}.csv"

    # Save the DataFrame to both Excel and CSV formats
    dataframe.to_excel(xlsx_filename, index=False)
    dataframe.to_csv(csv_filename, index=False)

    message = MIMEMultipart()
    message["From"] = EMAIL_SENDER
    message["To"] = ", ".join(CLIENT_EMAILS)
    message["Subject"] = "Doggles Monthly Inventory Report"

    body = ("Hello! Please find attached the latest Doggles monthly inventory "
            "report.\n\nThis is an automated email; please do not reply.\n\n"
            "For questions or orders, email info@doggles.com or call/text " 
            "(530) 344-1645.\n\n")
    
    message.attach(MIMEText(body, "plain"))

    with open(xlsx_filename, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=xlsx_filename)
        part["Content-Disposition"] = f'attachment; filename="{xlsx_filename}"'
        message.attach(part)
    
    with open(csv_filename, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=csv_filename)
        part["Content-Disposition"] = f'attachment; filename="{csv_filename}"'
        message.attach(part)

    # Send Email
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
