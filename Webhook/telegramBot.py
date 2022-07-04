import psycopg2
import requests
# https://api.telegram.org/bot{token}/{method}
#TODO need to save token of tg in separate file

def tg_action(text_var,method,chat_id):
    """this function call tg api"""
    url = r'https://api.telegram.org/bot{0}/{1}'.format(r'5539471875:AAE33eSniFYAJz7xvETV38t1ikrviPQDv6I', method)
    my_data = {"chat_id": chat_id, "text":text_var}
    response = requests.post(url, data=my_data).json()
    return response

def open_db_connection():
    """This function open db connection"""
    return psycopg2.connect(database="postgres", user="postgres", password="12345", host="db", port="5432")


def check_db_for_outdated_orders():
    """This function check for outdated orders in db and call tg_action. it's supposed to be called by CRON task."""
    conn = open_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT order_number,price,price_rub,date_of_supply FROM page_orders WHERE date_of_supply < current_date and notification  is not True ')
    records = cur.fetchall()
    cur.execute(
        'UPDATE page_orders SET notification=true WHERE date_of_supply < current_date and notification  is not True ')
    conn.commit()
    #print(records)
    message = None
    for row in records:
       # print(row)
        if not message:
            message= f"Hello,\nOrder number {row[0]} ({row[2]} RUB) is overdue. required date of supply was {row[3]}."
            print(message)
            tg_action(message, 'sendMessage', '618006496')
        else:
            message = f"Order number {row[0]} ({row[2]} RUB) is overdue. required date of supply was {row[3]}."
            print(message)
            tg_action(message, 'sendMessage', '618006496')
        #
    conn.close()

check_db_for_outdated_orders()