import os
import json
import sqlite3
import urllib.request
import xmltodict


# Функция получения курсов валют
class Read_curs:
    def __init__(self, date_cred, curr_code):
        self.text_error = ""
        try:
            file_settings = 'settings_curs_nbu.json'
            if not os.path.isfile(file_settings):
                self.text_error = "File 'settings_curs_nbu.json' not found"
                return

            # Opening JSON file
            f = open(file='settings_curs_nbu.json', mode="r", encoding="utf8")
            data = json.loads(f.read())
            f.close()
            self.data_format = data['main']['data_format']
            if self.data_format == 'json':
                self.file_name = data['main']['curs_nbu_json']['file_name']
                self.url = data['main']['curs_nbu_json']['url']
                self.char_curr_code = data['main']['curs_nbu_json']['char_curr_code']
                self.char_curr_name = data['main']['curs_nbu_json']['char_curr_name']
                self.char_curs = data['main']['curs_nbu_json']['char_curs']
                self.char_format_date = data['main']['curs_nbu_json']['char_format_date']
            elif self.data_format == 'xml':
                self.file_name = data['main']['curs_nbu_xml']['file_name']
                self.url = data['main']['curs_nbu_xml']['url']
                self.char_curr_code = data['main']['curs_nbu_xml']['char_curr_code']
                self.char_curr_name = data['main']['curs_nbu_xml']['char_curr_name']
                self.char_curs = data['main']['curs_nbu_xml']['char_curs']
                self.char_format_date = data['main']['curs_nbu_xml']['char_format_date']
            else:
                self.text_error = "File 'settings_curs_nbu.json' -> parameter 'data_format' not in 'xml' or 'json'"
                return

            # connect sqlite3
            con = sqlite3.connect("curs.db")
            cursor = con.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS CURS
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,  
                             CURS_DATE INTEGER NOT NULL, 
                             CURR_CODE TEXT NOT NULL,
                             RATE REAL NOT NULL CHECK(RATE > 0),
                             FORC INTEGER NOT NULL CHECK(FORC > 0)
                             )
                        """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS UK_CURS ON CURS (CURS_DATE, CURR_CODE)")

            cursor.execute("""CREATE TABLE IF NOT EXISTS CURRENCY
                            (CURR_CODE TEXT NOT NULL,
                             CURR_NAME TEXT)
                        """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS UK_CURRENCY ON CURRENCY (CURR_CODE)")

            # check curs
            self.is_request_curs = True
            params = (date_cred.strftime("%Y-%m-%d"), curr_code)
            cursor.execute("SELECT K.RATE/K.FORC AS CURS_AMOUNT, C.CURR_NAME "
                           "FROM CURS K, CURRENCY C "
                           "WHERE K.CURR_CODE = C.CURR_CODE AND K.CURS_DATE = ? AND K.CURR_CODE = ?", params)
            rows = cursor.fetchall()
            for row in rows:
                self.curs_amount = float(row[0])
                self.curr_name = row[1]
                self.is_request_curs = False

            if self.is_request_curs:
                # Read url
                url = self.url.replace("%MDATE%", date_cred.strftime(self.char_format_date)).replace("%CURRCODE%",
                                                                                                     curr_code)
                webURL = urllib.request.urlopen(url)
                data = webURL.read()

                if self.data_format == 'json':
                    JSON_object = json.loads(data.decode('utf-8'))
                    # write data
                    for json_line in JSON_object:
                        params = (date_cred.strftime("%Y-%m-%d"),
                                  json_line[self.char_curr_code],
                                  json_line[self.char_curs],
                                  1)
                        cursor.execute(
                            "INSERT OR IGNORE INTO CURRENCY(curr_code, curr_name) VALUES(?, ?)",
                            (json_line[self.char_curr_code], json_line[self.char_curr_name]))
                        cursor.execute(
                            "INSERT OR IGNORE INTO CURS(curs_date, curr_code, rate, forc) VALUES(?, ?, ?, ?)",
                            params)
                elif self.data_format == 'xml':
                    JSON_object = xmltodict.parse(data.decode('utf-8'))
                    # write data
                    json_line = JSON_object["exchange"]["currency"]
                    params = (date_cred.strftime("%Y-%m-%d"),
                              json_line[self.char_curr_code],
                              json_line[self.char_curs],
                              1)
                    cursor.execute("INSERT OR IGNORE INTO CURRENCY(curr_code, curr_name) VALUES(?, ?)",
                                   (json_line[self.char_curr_code], json_line[self.char_curr_name]))
                    cursor.execute("INSERT OR IGNORE INTO CURS(curs_date, curr_code, rate, forc) VALUES(?, ?, ?, ?)",
                                   params)

                # read new curs
                params = (date_cred.strftime("%Y-%m-%d"), curr_code)
                cursor.execute("SELECT K.RATE/K.FORC AS CURS_AMOUNT, C.CURR_NAME "
                               "FROM CURS K, CURRENCY C "
                               "WHERE K.CURR_CODE = C.CURR_CODE AND K.CURS_DATE = ? AND K.CURR_CODE = ?", params)
                rows = cursor.fetchall()
                for row in rows:
                    self.curs_amount = float(row[0])
                    self.curr_name = row[1]
                    self.is_request_curs = False

            con.commit()
            con.close()
        except Exception as err_curs:
            self.text_error = err_curs
