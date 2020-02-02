FROM python:3.7

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip3 install --upgrade pip && \
    pip3 install flask && \
    pip3 install -r requirements.txt
COPY . .

EXPOSE 3000
CMD ["python3", "main.py"]