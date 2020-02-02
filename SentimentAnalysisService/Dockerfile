FROM tensorflow/tensorflow 

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install flask && \
    pip install -r requirements.txt
COPY . .

EXPOSE 80
CMD ["python", "main.py"]