import os
import json
import time
import logging
from flask import Flask, request
from sentiment import Sentiment
from kafka import KafkaProducer, KafkaClient
from kafka.errors import NoBrokersAvailable

# Create a logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info('Initialization...')
# Check whether topic is set, otherwise use Tweet
topic = os.environ.get('TOPIC') or 'tweet'

# Load the Keras model and weights
logger.info('Create sentiment module...')
sentiment = Sentiment(logger)
sentiment.loadWordIndex()
sentiment.loadWeights(os.environ['SENTIMENT_WEIGHTS'])
# Test the prediction once
logger.info('Test prediction...')
sentiment.predict('Test if this instance work...')

# Check if Kafka is reachable and if the kafka topic was created
logger.info('Wait for Kafka broker and "' + topic + '" topic...')
kafkaTopics = []
while topic not in kafkaTopics:
    try:
        client = KafkaClient(os.environ['KAFKA_HOST'])
        kafkaTopics = client.topic_partitions
        client.close()
        logger.info('Topic ' + topic + ' not available - wait 2 sec...')
        time.sleep(2)
    except NoBrokersAvailable as err:
        logger.error("Unable to find a broker: {0}".format(err))
        time.sleep(1)
logger.info('Kafka broker and topic available.')

# Create the Kafka producer
logger.info('Producer connect to Kafka broker...')
producer = KafkaProducer(bootstrap_servers=os.environ['KAFKA_HOST'])

# Create an api with Flask
logger.info('Create HTTP-Interface...')
app = Flask(__name__)

# Get: Return running information
@app.route("/", methods=['GET'])
def index():
    return "Running..."

# Post: Extract text, analyse it and push the tweet with the additional information to Kafka
@app.route("/", methods=['POST'])
def post_event():
    data = request.get_json()
    data['sentiment'] = sentiment.predict(data['text'])
    data = json.dumps(data)
    producer.send(topic, bytes(data.encode('utf-8')))
    logger.info('Tweet - [' + topic + ']: ' + data)
    return json.dumps({'status': 'ok'}), 200


# Run API
if __name__ == '__main__':
    logger.info('Listen on port 80')
    app.run(host='0.0.0.0', port=80, debug=True)