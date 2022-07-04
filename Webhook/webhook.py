from __future__ import print_function

from __future__ import print_function

import os
import time
import requests
import os.path
import psycopg2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import ngrok
from flask_ngrok import run_with_ngrok
import pytz
# TODO need to create separate file with credentials of DB and ngrok token,

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'


def open_db_connection():
    """This function open db connection"""
    return psycopg2.connect(database="postgres", user="postgres", password="12345", host="db", port="5432")


def get_current_usd_rate():
    """This function return current USD rate using cbr api"""
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return data['Valute']['USD']['Value']



def update_table():
    """This function connects to Google Sheets Api and retrieve all records, checks with regex for corrects ones and save them to PSQL,
    if it's finds that order was removed from GSheets it's only mark it as removed in DB for possible future use and analysis.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=r'1nmYlA6X2tncvq9XQhSqtWVqLtoLWUfSHpM-qOrnMjrg',
                                    range='Лист1!A2:D100').execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        values= [x for x in values if (len(x)==4 and re.match(r"\d+", x[0]) and re.match(r"\S", x[1]) and re.match(r"\d+(.\d+)?", x[2]) and re.match(r"\d{2}.\d{2}.\d{4}", x[3]) )]
        order_list = [x[1] for x in values]
        print(order_list)
        current_usd_rate= get_current_usd_rate()
        try:
            conn = open_db_connection()
            cur = conn.cursor()
            # cur.execute('DROP TABLE page_orders;')
            # conn.commit()
            # exit()
            time.sleep(5)
            #cur.execute(
            #     "CREATE TABLE page_orders(id integer, order_number integer PRIMARY KEY, price real,price_rub real, date_of_supply date, removed boolean, notification boolean);")
            print("Table Created....")
            #cur.execute('DROP TABLE last_orders;')
            cur.execute("CREATE TABLE last_orders(order_number integer PRIMARY KEY);")
            conn.commit()
            print("Table Created 2....")
            for row in values:
                try:
                    cur.execute("INSERT INTO last_orders ( order_number) VALUES (%s)" % (row[1]))
                    conn.commit()
                    cur.execute("INSERT INTO page_orders (id, order_number, price,price_rub, date_of_supply, removed, notification) \
                  VALUES (%s, %s, %s, %s, %s, %s, %s)" % (row[0], row[1], row[2], round(float(row[2])*current_usd_rate,2), "'%s'"% datetime.strptime(row[3],'%d.%m.%Y').strftime('%Y-%m-%d'),False, False));
                except psycopg2.errors.UniqueViolation:
                    conn.commit()
                    try:
                        print("UPDATE page_orders SET id = %s, price=%s,price_rub=%s, date_of_supply=%s  WHERE order_number = %s" % (row[0], row[2], round(float(row[2]) * current_usd_rate, 2),
                                                    "'%s'" % datetime.strptime(row[3], '%d.%m.%Y').strftime(
                                                        '%Y-%m-%d'), row[1]))
                        cur.execute("UPDATE page_orders SET id = %s, price=%s,price_rub=%s, date_of_supply=%s  WHERE order_number = %s" % (row[0], row[2], round(float(row[2]) * current_usd_rate, 2),
                                                    "'%s'" % datetime.strptime(row[3], '%d.%m.%Y').strftime(
                                                        '%Y-%m-%d'), row[1]));
                    except BaseException as err:
                        print(type(err))
            conn.commit()
            cur.execute("UPDATE page_orders SET removed=true  where page_orders.order_number::integer not in (select last_orders.order_number  FROM last_orders JOIN page_orders ON page_orders.order_number::varchar = last_orders.order_number::varchar); " );
            cur.execute(
                "UPDATE page_orders SET removed=false  where page_orders.order_number::integer in (select last_orders.order_number  FROM last_orders JOIN page_orders ON page_orders.order_number::varchar = last_orders.order_number::varchar); ");
            cur.execute('DROP TABLE last_orders;')
            conn.commit()
            conn.close()
        except BaseException as err:
            print(err)
            conn.close()
    except HttpError as err:
        print(err)
        conn.close()




SCOPES = ['https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive.readonly',
         'https://www.googleapis.com/auth/drive']


def fetch_changes(saved_start_page_token,addr):
    """Retrieve the list of changes for the currently authenticated user.
        prints changed file's ID
    Args:
        saved_start_page_token : StartPageToken for the current state of the
        account.
    Returns: saved start page token.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        # Begin with our last saved start token for this user or the
        # current token from getStartPageToken()
        page_token = saved_start_page_token
        # pylint: disable=maybe-no-member

        while page_token is not None:
            body = {
                'id': 'ngrok_webhook123243',
                'type': "web_hook",
                'address': addr
            }

            response = service.files().watch(fileId="1nmYlA6X2tncvq9XQhSqtWVqLtoLWUfSHpM-qOrnMjrg", body=body).execute()

            print(response)
    except HttpError as error:
        print(F'An error occurred: {error}')
        saved_start_page_token = None

    return saved_start_page_token


def create_webhock(addr):
    # saved_start_page_token is the token number
    fetch_changes(saved_start_page_token=209, addr=addr)


#create_webhock()


def get_timestamp():
    """
    This function creates current timestamp in predefined format.
    """
    dt=datetime.now(pytz.timezone('US/Central'))
    return dt.strftime(("%Y-%m-%d %H:%M:%S"))





ngrok.set_auth_token("2BIpQLR4wReSkTXEffcniRJSs7j_7ukAceYqC9ehWqBbLv16V")
http_tunnel = ngrok.connect(5000)
print('test', http_tunnel.public_url)
#
create_webhock(str(http_tunnel.public_url).replace('http','https'))


def get_timestamp():
    dt=datetime.now(pytz.timezone('US/Central'))
    return dt.strftime(("%Y-%m-%d %H:%M:%S"))
update_table()

app = Flask(__name__)
app.config["BASE_URL"] = http_tunnel.public_url
run_with_ngrok(app)
@app.route('/webhook', methods=['POST','GET'])
def webhook():
    """
    This function waits for call from GoogleSheet and runs table update once received it.
    """
    if request.method=='GET':
        return '<h1>  This is a webhook listener! You should send POST request in order to trigger it.</h1>'
    if request.method == 'POST':
        print(request.headers)
        cur_date=get_timestamp()
        print("Date and time of update ====>",cur_date)
        http_status=jsonify({'status':'success'}),200
        update_table()
    else:
        update_table()
        http_status='',400
    return http_status

if __name__ == '__main__':
     app.run() #