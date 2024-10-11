"""
This module provides handles errors by sending email notifications.

Functions:
- handle_errors(message): Formats and sends email with details of the failure.
- send_email(failure): Send an error notification email with details of the failure.
- send_with_smtp(sender_email, sender_password, recipient_emails, subject, message).
- format_err_msg(e): Generate a formatted error message including the traceback.
- get_object_id(link): Extract and return the object ID from a Catawiki link.
"""

# pylint: disable=W0718

import sys
import json
import traceback
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from auctionsscraper.error_messages import (error_msg)
from auctionsscraper.items import DescriptionItem

import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

from scrapy.loader import ItemLoader


def load_json_data(file_path):
    """Load data from a JSON file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' was not found.")

        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Add this line to debug
                print(f"Loaded data from {file_path}: {data}")
                return data
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Failed to decode JSON from '{file_path}'. The file may be corrupted or is not in JSON format.") from e
    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except PermissionError:
        print(f"Permission denied while trying to read '{file_path}'.")
    except IOError as io_error:
        print(
            f"An I/O error occurred while accessing '{file_path}': {io_error}")


def handle_error(message):
    """Handle errors by sending an email with the error message and stopping the spider."""
    send_email(format_err_msg(message))


def send_email(failure):
    """
    Send an error notification email with details of the failure.

    Args:
    failure (str): Description of the error that occurred.

    Returns:
    None
    """
    sender_email = "itgoal@itgoal.pl"
    # Store securely, consider using environment variables
    sender_password = "R3b3lia22#"
    # Update with actual recipient emails
    recipient_emails = ["patryk.mauer@gmail.com"]
    subject = "CatawikiScraper Error Notification"
    checkout = "Checkout this project: https: // github.com/PatrykMauer/CatawikiScraper"
    message = f"An error occurred during scraping: {failure} + '\n' + {checkout}"

    # Call the send_email function with error details
    send_with_smtp(sender_email, sender_password,
                   recipient_emails, subject, message)


def send_with_smtp(
        sender_email, sender_password, recipient_emails, subject, message):
    """
    Send an email using SMTP.

    Args:
    sender_email (str): Email address of the sender.
    sender_password (str): Password of the sender's email account.
    recipient_emails (list): List of recipient email addresses.
    subject (str): Subject of the email.
    message (str): Body of the email.

    Returns:
    None
    """
    smtp_server = "smtp.dpoczta.pl"
    smtp_port = 587

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        for recipient_email in recipient_emails:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'html'))

                server.sendmail(sender_email, recipient_email, msg.as_string())
                print(f"Email sent to {recipient_email} successfully!")
            except smtplib.SMTPRecipientsRefused:
                print(
                    f"All recipients were refused for email to {recipient_email}.")
            except smtplib.SMTPHeloError:
                print(
                    f"Server did not reply properly to the HELO for email to {recipient_email}.")
            except smtplib.SMTPSenderRefused:
                print(
                    f"Sender address refused for email to {recipient_email}.")
            except smtplib.SMTPDataError:
                print(
                    f"The SMTP server refused to the message data for email to {recipient_email}.")
            except smtplib.SMTPException as e:
                print(
                    f"SMTP error occurred while sending email to {recipient_email}: {str(e)}")

        server.quit()
    except smtplib.SMTPConnectError:
        print("Could not connect to SMTP server.")
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed.")
    except smtplib.SMTPException as e:
        print(f"An SMTP error occurred: {str(e)}")
    except Exception as e:
        # Fallback for any other SMTP-related errors not covered
        print(f"An unexpected error occurred: {str(e)}")


def format_err_msg(e):
    """
    Generates a formatted error message including the traceback.

    Args:
    e (Exception): The exception object caught in the try-except block.

    Returns:
    str: A formatted string containing details about the exception and its traceback.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    trace_info = traceback.format_exception(exc_type, exc_value, exc_traceback)
    trace_string = ''.join(trace_info)
    return f"An error occurred: {str(e)}\n{trace_string}"


def get_object_id(link):
    """
    Extract and return the object ID from a Catawiki link.

    Args:
    link (str): The Catawiki link.

    Returns:
    str: The object ID extracted from the link.
    """
    return link[30:38]


unit_conversion_ratios = {
    'cm': 1.0,
    'mm': 0.1,
    'in': 2.54,
    'ft': 30.48,
    'yd': 91.44,
    'mi': 160934.4,
    'm': 100
}


def get_total_dimensions(object_dict):
    """
    Creates dimension string.
    """
    if 'Total dimensions' not in object_dict:
        height, height_unit = extract_dimension(
            object_dict.get('Height', ''))
        width, width_unit = extract_dimension(
            object_dict.get('Width', ''))
        depth, depth_unit = extract_dimension(
            object_dict.get('Depth', ''))

        if height is not None and width is not None and depth is not None:
            height_in_cm = convert_to_cm(height, height_unit)
            width_in_cm = convert_to_cm(width, width_unit)
            depth_in_cm = convert_to_cm(depth, depth_unit)

            total_dimensions = f"{height_in_cm}x{width_in_cm}x{depth_in_cm} cm"
            object_dict['Total dimensions'] = total_dimensions


def extract_dimension(dimension):
    """
    Extracts a dimension value and its unit from a given string.
    """
    if dimension:
        for unit in ['cm', 'mm', 'in', 'ft', 'yd', 'mi', 'm']:
            if dimension.endswith(unit):
                numeric_value = float(dimension.replace(unit, '').strip())
                converted_value = round(
                    numeric_value * unit_conversion_ratios[unit], 2)
                return converted_value, unit
    return dimension, 'cm'


def convert_to_cm(value, unit):
    """
    Converts a dimension value from a given unit to centimeters.
    """
    return round(value * unit_conversion_ratios[unit], 2)


def merge_data(objects_data, specs_data):
    """Merge object data with specifications data based on matching IDs."""
    merged_data = {}
    for obj in objects_data:
        obj_id = str(obj['id'])  # Convert object ID to string if not already
        for spec in specs_data:
            if 'id' in spec['object'] and obj_id == str(spec['object']['id']):
                # Ensure spec ID is also converted to string before comparing
                obj.update(spec['object'])
                merged_data[obj_id] = obj
                break
            elif 'id' not in spec['object']:
                # Log missing 'id'
                print(f"Warning: Missing 'id' in spec {spec}")
    return merged_data


def initialize_google_sheets():
    """Initialize Google Sheets client using credentials from 'credentials.json'."""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json',
        scope)
    client = gspread.authorize(creds)
    return client


def send_data_to_flask_app(flask_url, df, filename):
    """Send data and filename to the Flask app via a POST request."""
    try:
        # Convert DataFrame to JSON format
        data_json = df.to_json(orient='records')

        # Prepare the payload with both data and filename
        payload = {
            'filename': filename,  # The file name to send with the data
            'data': data_json       # The actual data to append
        }

        # Send POST request to Flask app
        response = requests.post(flask_url, json=payload)

        # Check for successful response
        if response.status_code == 200:
            print("Data sent successfully to Flask app.")
        else:
            print(
                f"Failed to send data to Flask app: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending data to Flask app: {e}")


def upload_to_google_sheets(client, df, sheet_url, sheet_name):
    """Upload data to a specified Google Sheets URL and sheet name."""
    try:
        sheet = client.open_by_url(sheet_url).sheet1

        needed_rows = len(df.index)
        print(f"Adding {needed_rows} rows to the sheet.")

        first_empty_row = sheet.row_count + 1

        sheet.add_rows(needed_rows)
        sheet = client.open_by_url(sheet_url).sheet1

        if sheet.row_count == needed_rows+1:
            set_with_dataframe(
                sheet, df, include_index=False, include_column_header=True,
                resize=False)
        else:
            set_with_dataframe(
                sheet, df, include_index=False, include_column_header=False,
                row=first_empty_row, resize=False)
        print("Data uploaded successfully.")

    except Exception as e:
        print(f"Failed to upload data to Google Sheets: {e}")


def prepare_data_for_sheet(merged_data, columns):
    """Prepare data for Google Sheets by extracting specified columns."""
    return [[obj.get(col, '') for col in columns] for obj in merged_data.values()]


def save_data_to_json(merged_data, file_name):
    """Save merged data to a JSON file."""
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(list(merged_data.values()), f, ensure_ascii=False)


def extract_id_from_url(response):
    """Extract and return the last 8 characters of the URL."""
    return response.url[-8:]


def extract_specifications(response):
    """Extract specifications from JSON data embedded in a script tag."""
    json_script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
    json_data = json.loads(json_script)
    return json_data["props"]["pageProps"]["lotDetailsData"].get(
        "specifications", [])


def append_specifications_to_details(specifications):
    """Append specifications to the object details list."""
    details = []
    for spec in specifications:
        details.append(
            {'name': spec.get("name", ""),
             'value': spec.get("value", "")})
    return details


def load_description(response):
    """Load and return the description using ItemLoader."""
    loader = ItemLoader(item=DescriptionItem(), selector=response)
    loader.add_css(
        'Description', 'div.lot-info-description__description p::text')
    return loader.load_item()


def merge_details_with_description(object_details, description):
    """Merge object details with description and return as a dictionary."""
    object_dict = {detail['name']: detail['value']
                   for detail in object_details}
    object_dict.update(description)
    return object_dict
