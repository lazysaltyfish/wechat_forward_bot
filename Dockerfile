FROM --platform=linux/arm64 python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "pypy3", "./main.py" ]