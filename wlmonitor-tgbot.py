import os
import telebot
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Path to credentials JSON file
CREDENTIALS_FILE = 'path/creds.json'

# Google Sheets Document ID
GSH_DOCUMENT_ID = "GSH_DOCUMENT_ID"

# Authenticate using OAuth 2.0 credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets'])
client = gspread.authorize(credentials)

# Open the spreadsheet by document ID
sh = client.open_by_key(GSH_DOCUMENT_ID)

# Select the first sheet
worksheet = sh.get_worksheet(0)  # Index 0 represents the first sheet

def update_sheet_with_data(row_data):
    # Specify range in sheet
    range = 'A1:C'
    
    # Append the data to the sheet
    worksheet.append_row(row_data, table_range=range, value_input_option='USER_ENTERED', insert_data_option='OVERWRITE')

def is_weight_record_exists(date_str, name):
    range = 'A2:B' # range of cells in the sheet to take values from
    weight_records = worksheet.get(range)
    return [date_str, name] in weight_records

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    #bot.reply_to(message, "Hi! Add your today weight using the add command followed by weight in '55.5' format. For example '/add 55.5'")
    bot.send_message(chat_id=message.chat.id, text="Hi\! Add your today weight using the *'add'* command followed by weight in *'55\.5'* format\. For example *'/add 55\.5'*", parse_mode="MarkdownV2", reply_to_message_id = message.id)

@bot.message_handler(func=lambda msg: True)
def reply(message):
    pattern = r'/add (\d{2}\.\d)'
    if re.match(pattern, message.text) is not None and len(message.text) == 9:
        weight = re.match(pattern, message.text).group(1)
        name = 'User 1' if float(weight) < 75 else 'User 2'
        today_date = str(date.today())
        # Check if weight record for provided date and name already exists
        if is_weight_record_exists(today_date, name):
            bot.reply_to(message, f"Weight record already exists! {[today_date, name]}. Correct values in the file and try again.")
        else:
            # Data in the row to append to the sheet
            row_data = [today_date, name, weight]
            update_sheet_with_data(row_data)
            bot.reply_to(message, f"Weight recorded successfully! Recorded data: {row_data}")
    else:
        bot.reply_to(message, "Wrong input. Please, enter your weight using the add command followed by weight in '55.5' format. For example '/add 55.5'")

bot.infinity_polling()
