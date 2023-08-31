import requests


# Функция получения с Единого реестра должников исполнительных производств
class Read_erb:
    def __init__(self, cust_type, cust_params):
        self.text_error = ""
        self.text_result = ""
        self.count_result = 0
        try:
            url = 'https://erb.minjust.gov.ua/listDebtorsEndpoint'
            if cust_type == 'phys':
                if cust_params[4] is not None:
                    # преобразование 01.02.2001 -> 2001-02-01T00:00:00.000Z
                    data = str(cust_params[4])
                    data = data[6:10] + "-" + data[3:5] + "-" + data[0:2] + "T00:00:00.000Z"
                else:
                    data = None
                m_json = {"filter": {"IdentCode": cust_params[0],
                                     "LastName": cust_params[1],
                                     "FirstName": cust_params[2],
                                     "MiddleName": cust_params[3],
                                     "BirthDate": data,
                                     "categoryCode": ""},
                          "paging": "1", "searchType": "1"}
            elif cust_type == 'jur':
                m_json = {"filter": {"FirmEdrpou": cust_params[0],
                                     "FirmName": cust_params[1],
                                     "categoryCode": ""},
                          "paging": "1", "searchType": "2"}
            else:
                self.text_error = 'Ошибка = тип контрагента не верный = ' + str(cust_type)
                return

            response = requests.post(url, json=m_json)
            if response.status_code == 200:
                m_json = response.json()
                if m_json['isSuccess']:
                    m_buff = ""
                    self.count_result = m_json['rows']
                    m_buff_start = ("Знайдено: " + str(m_json['rows']) + ' виконавчих проваджень, опис перших 5-ти:'
                                    + "\n" + "\n")
                    for cc_num, cc in enumerate(m_json["results"]):
                        if cc_num >= 5:
                            break
                        # результаты
                        if cust_type == 'phys':
                            # преобразование 2001-02-01T00:00:00.000Z -> 01.02.2001
                            data = str(cc['birthDate'])
                            data = data[8:10] + "." + data[5:7] + "." + data[0:4]
                            m_buff = ("ПІБ: " + (str(cc['lastName']) + " " + str(cc['firstName']) + " " + str(
                                cc['middleName'])).strip() + "\n"
                                      + 'Дата нар.: ' + data + "\n"
                                      + 'Опис: ' + str(cc['deductionType']) + "\n"
                                      + 'Тип: ' + str(cc['publisher']) + "\n"
                                      + 'Тел: ' + str(cc['executorPhone']) + "\n"
                                      + '№ провадження:: ' + str(cc['vpNum']) + "\n"
                                      )
                        elif cust_type == 'jur':
                            m_buff = ("Найм: " + str(cc['name']) + "\n"
                                      + 'ЄДРПОУ: ' + str(cc['code']) + "\n"
                                      + 'Опис: ' + str(cc['deductionType']) + "\n"
                                      + 'Тип: ' + str(cc['publisher']) + "\n"
                                      + 'Тел: ' + str(cc['executorPhone']) + "\n"
                                      + '№ провадження:: ' + str(cc['vpNum']) + "\n"
                                      )
                        if self.text_result == "":
                            self.text_result = m_buff_start + m_buff
                        else:
                            self.text_result = self.text_result + "\n" + m_buff
                    print(self.text_result)
            else:
                self.text_error = 'Ошибка = ' + response.text

        except Exception as err_curs:
            self.text_error = err_curs
            print(self.text_error)
