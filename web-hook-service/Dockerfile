FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY . .

RUN pip3.8 install --upgrade pip
RUN pip3.8 install -r requirements.txt
RUN python3.8 app/test_flask.py

CMD ["python3.8", "app/main.py"]
