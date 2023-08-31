from currency_converter import CurrencyConverter


# Функция реализации конвертации курсов валют
class Read_convert_curs:
    def __init__(self, amount, curr_code_from, curr_code_to):
        self.text_error = ""
        try:
            curr_converter = CurrencyConverter()
            self.curs_amount = curr_converter.convert(amount, curr_code_from, curr_code_to)

        except Exception as err:
            self.text_error = err
