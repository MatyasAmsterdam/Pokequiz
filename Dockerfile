FROM python:3.11.2

COPY . /

RUN pip install -r requirements.txt

CMD ["flask", "--app", "application", "run", "--host=0.0.0.0"]
