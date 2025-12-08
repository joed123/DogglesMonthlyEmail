#### Shopify Inventory Reporter
This Python script automatically fetches the current, in-stock inventory for products from a specified Shopify store, processes the data, and emails a filtered report in both Excel (.xlsx) and CSV (.csv) formats to a list of specified recipients.

## Features
Shopify API Integration: Connects securely to the Shopify Storefront API.

Inventory Filtering: Only includes products/variants that currently have a quantity greater than zero.

Data Export: Saves the final report as both an Excel (.xlsx) and CSV (.csv) file.

Automated Emailing: Uses SMTP (e.g., Gmail) to send the report with both files attached.

Pandas Utilization: Efficiently processes and formats the data using the pandas library.

