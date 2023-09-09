import csv
import json
import sqlite3
import urllib.request
import urllib.error
from datetime import date


def get_name_securities_type(securities_type):
    m = {
        '1': 'Довгострокові',
        '2': 'Довгострокові з індексованою вартістю',
        '3': 'Довгострокові інфляційні',
        '4': 'Середньострокові',
        '5': 'Короткострокові дисконтні',
        '6': 'OЗДП%'
    }
    try:
        securities_name = m[securities_type]
    except Exception as err:
        securities_name = securities_type
        print(err)
    return securities_name


# Функция получения данных о ценных бумагах
class Read_ISIN_Securities:
    def __init__(self, securities_type, curr_code, securities_isin, is_coup_period):
        self.text_error = ""
        self.text_result = ""
        con = None
        try:
            # connect sqlite3
            con = sqlite3.connect("./database/securities.db")
            cursor = con.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS SECUR_ISIN
                    (ID INTEGER PRIMARY KEY 
                    AUTOINCREMENT NOT NULL,                               
                     ISIN TEXT NOT NULL,
                     NOMINAL INTEGER NOT NULL,
                     AUK_PROC REAL NOT NULL,
                     PGS_DATE INTEGER NOT NULL,
                     CPDESCR TEXT NOT NULL,
                     CURRENCY_CODE TEXT NOT NULL,
                     SDATE INTEGER NOT NULL,
                     FAIR_DATE INTEGER,
                     FAIR_VALUE REAL
                     )
                """)
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "UK_SECUR_ISIN ON SECUR_ISIN (ISIN)")

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS SECUR_ISIN_PAY
                (ID INTEGER PRIMARY KEY 
                AUTOINCREMENT NOT NULL,                               
                 ISIN_SECUR_ID INTEGER NOT NULL,
                 PAY_DATE INTEGER NOT NULL,
                 PAY_TYPE INTEGER NOT NULL,
                 PAY_VAL REAL NOT NULL,
                 FOREIGN KEY(ISIN_SECUR_ID) 
                 REFERENCES SECUR_ISIN(ID)                           
                 )
            """)
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS UK_SECUR_ISIN_PAY "
                "ON SECUR_ISIN_PAY (ISIN_SECUR_ID, "
                "PAY_DATE, PAY_TYPE)")

            # проверяем есть ли обновленные данные по ISIN ЦБ
            # за текущий день, если нет перезаливаем
            params = (date.today().strftime("%Y-%m-%d"),)
            cursor.execute(
                "SELECT COUNT(*) AS KOL FROM SECUR_ISIN S "
                "WHERE S.SDATE = ?", params)
            rows = cursor.fetchone()
            # если нет данных загрузить их
            if rows[0] == 0:
                url = urllib.request.urlopen("https://bank.gov.ua/depo_securities?json")
                data = url.read()
                JSON_object = json.loads(data.decode('utf-8'))
                # write data
                for json_line in JSON_object:
                    # возвращаем ID
                    params = (json_line['cpcode'],)
                    cursor.execute(
                        "SELECT COUNT(*) AS KOL, MAX(ID) AS ID "
                        "FROM SECUR_ISIN S WHERE S.ISIN = ?", params)
                    rows = cursor.fetchone()
                    if rows[0] == 0:
                        params = (json_line['cpcode'],
                                  json_line['nominal'],
                                  json_line['auk_proc'],
                                  json_line['pgs_date'],
                                  json_line['cpdescr'],
                                  json_line['val_code'],
                                  date.today().strftime("%Y-%m-%d")
                                  )
                        cursor.execute(
                            'INSERT INTO SECUR_ISIN(ISIN, NOMINAL, AUK_PROC, '
                            'PGS_DATE, CPDESCR, CURRENCY_CODE, SDATE)'
                            ' VALUES(?, ?, ?, ?, ?, ?, ?)', params)

                        params = (json_line['cpcode'],)
                        cursor.execute(
                            "SELECT COUNT(*) AS KOL, MAX(ID) AS ID FROM SECUR_ISIN S "
                            "WHERE S.ISIN = ?", params)
                        rows = cursor.fetchone()
                        inserted_id = rows[1]
                    else:
                        inserted_id = rows[1]
                        params = (date.today().strftime("%Y-%m-%d"),
                                  inserted_id)
                        cursor.execute(
                            'UPDATE SECUR_ISIN SET SDATE = ? WHERE ID = ?', params)

                    # купонные периоды
                    for json_line2 in json_line['payments']:
                        params = (inserted_id,
                                  json_line2['pay_date'],
                                  json_line2['pay_type'],
                                  json_line2['pay_val']
                                  )
                        cursor.execute(
                            "INSERT OR IGNORE INTO SECUR_ISIN_PAY"
                            "(ISIN_SECUR_ID, PAY_DATE, PAY_TYPE, PAY_VAL)"
                            " VALUES(?, ?, ?, ?)", params)

            # Справедливая стоимость ЦБ (котировки НБУ)
            params = (date.today().strftime("%Y-%m-%d"),)
            cursor.execute(
                "SELECT COUNT(*) AS KOL FROM SECUR_ISIN S "
                "WHERE S.FAIR_DATE = ?", params)
            rows = cursor.fetchone()
            # если нет данных загрузить их и обновить
            if rows[0] == 0:
                try:
                    url = ("https://bank.gov.ua/files/Fair_value/" +
                           date.today().strftime("%Y%m") + "/" +
                           date.today().strftime("%Y%m%d") + "_fv.txt")
                    response = urllib.request.urlopen(url)
                    lines = [line.decode('cp1251') for line in response.readlines()]
                    cr = csv.reader(lines)
                    for row in cr:
                        split_data = row[0].split(";")
                        if split_data[1] == "cpcode":
                            continue
                        params = (date.today().strftime("%Y-%m-%d"),
                                  float(split_data[3]),
                                  split_data[1])
                        cursor.execute(
                            'UPDATE SECUR_ISIN SET FAIR_DATE = ?, FAIR_VALUE = ? '
                            'WHERE ISIN = ?', params)
                except urllib.error.HTTPError as e:
                    if e.code != 404:
                        raise
            # Получить данные
            if securities_isin == "":
                securities_name = get_name_securities_type(securities_type)
                params = (securities_name, curr_code)
                if securities_name.find("%") >= 0:
                    cursor.execute(
                        "SELECT * FROM SECUR_ISIN S WHERE S.CPDESCR like ? "
                        "AND S.CURRENCY_CODE = ?", params)
                else:
                    cursor.execute(
                        "SELECT * FROM SECUR_ISIN S WHERE S.CPDESCR = ? "
                        "AND S.CURRENCY_CODE = ?", params)
                rows = cursor.fetchall()
            else:
                params = (securities_isin,)
                cursor.execute("SELECT * FROM SECUR_ISIN S WHERE S.ISIN = ?", params)
                rows = cursor.fetchall()
            buff = ""
            for row_count, row in enumerate(rows):
                if row[9] is None:
                    fair_value = "--"
                else:
                    if row[8] is None or row[8] == date.today().strftime("%Y-%m-%d"):
                        fair_value = str(row[9])
                    else:
                        fair_value = str(row[9]) + " за " + str(row[8])
                buff = buff + ("ISIN: " + str(row[1]) + "\n"
                               + "Номінал: " + str(row[2]) + "\n"
                               + "Вартість: " + fair_value + "\n"
                               + "Валюта: " + str(row[6]) + "\n"
                               + "% ставка: " + str(row[3]) + "\n"
                               + "Дата виплати: " + str(row[4]) + "\n"
                               )
                # купонные периоды
                if is_coup_period:
                    params = (row[0],)
                    cursor.execute(
                        "SELECT * FROM SECUR_ISIN_PAY S WHERE "
                        "S.ISIN_SECUR_ID = ? AND S.PAY_TYPE = 1 "
                        "ORDER BY S.PAY_DATE",
                        params)
                    rows2 = cursor.fetchall()
                    if len(rows2) > 0:
                        buff = buff + "Купонні періоди:" + "\n"
                    for row2 in rows2:
                        buff = buff + "- " + str(row2[2]) + " = " + str(row2[4]) + "\n"
                buff = buff + "\n"

            con.commit()
            con.close()

            self.text_result = buff
        except Exception as err_message:
            con.close()
            self.text_error = err_message
            print(err_message)
