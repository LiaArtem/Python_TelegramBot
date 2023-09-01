FROM python:latest

# set work directory
WORKDIR /usr/src/app/

# copy project
COPY ./*.py /usr/src/app/
COPY ./*.json /usr/src/app/

# install dependencies
RUN pip install pyTelegramBotAPI
RUN pip install emoji
RUN pip install xmltodict
RUN pip install CurrencyConverter

# run app
CMD ["python", "main.py"]