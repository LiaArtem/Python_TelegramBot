FROM python:latest

# set work directory
WORKDIR /usr/src/app/

RUN mkdir -p /usr/src/app/service/
RUN mkdir -p /usr/src/app/database/
RUN mkdir -p /usr/src/app/log/
# copy project
COPY ./*.py /usr/src/app/
COPY ./service/*.py /usr/src/app/service/
COPY ./database/*.json /usr/src/app/database/
COPY ./secret_key /usr/src/app/


# install dependencies
RUN pip install pyTelegramBotAPI
RUN pip install emoji
RUN pip install xmltodict
RUN pip install CurrencyConverter
RUN pip install requests
RUN pip install environs

# run app
CMD ["python", "main.py"]