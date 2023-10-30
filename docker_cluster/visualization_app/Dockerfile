FROM python:3.11-slim

USER root

RUN mkdir /app
COPY ./src /app
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8501
WORKDIR /app

CMD streamlit run app.py


