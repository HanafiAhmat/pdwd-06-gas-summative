FROM python:3.12.8-slim

WORKDIR /var/www/app

RUN apt update
RUN apt install pkg-config python3-dev default-libmysqlclient-dev build-essential -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

EXPOSE 8000

COPY --chmod=0755 docker/python/start.sh /start.sh

CMD /start.sh
# CMD [ "python", "/var/www/app/manage.py", "migrate" ]
# CMD [ "python", "/var/www/app/manage.py", "runserver", "0.0.0.0:8000" ]
