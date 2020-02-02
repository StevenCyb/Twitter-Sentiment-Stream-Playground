import os
import time
import json
import logging
import splunklib.client as SplunkClient
from kafka import KafkaConsumer, KafkaClient, TopicPartition
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
topic = os.environ.get('KAFKA_TOPIC') or 'tweet'

# Check if Splunk is reachable 
logger.info('Connect to Splunk...')
splunk = None 
while splunk is None:
    try:
        splunk = SplunkClient.connect(
            host=os.environ.get('SPLUNK_HOST').split(':')[0],
            port=int(os.environ.get('SPLUNK_HOST').split(':')[1]),
            username=os.environ.get('SPLUNK_USERNAME'),
            password=os.environ.get('SPLUNK_PASSWORD')
        )
    except:
        logger.error("Connection to Splunk failed. Retry in 1 sec.")
        time.sleep(1)

# Create a topic when not exists  
if topic not in splunk.indexes:
    logger.info('Create index ' + topic + ' on Splunk...')
    splunk.indexes.create(topic)

# Select index of the topic
splunkIndex = splunk.indexes[topic]

# Check if Kafka is reachable and if the kafka topic was created
logger.info('Wait for Kafka broker and ' + topic + ' topic...')
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
logger.info('Topic available.')

# Create a consumer
logger.info('Consumer connect to Kafka broker...')
consumer = KafkaConsumer(
    bootstrap_servers=os.environ['KAFKA_HOST'],
    consumer_timeout_ms=200,
    auto_offset_reset='earliest',
    group_id=None
)

# Subscribe the topic on Kafka
logger.info('Consumer prepair...')
consumer.subscribe(topic)
consumer.poll(timeout_ms=10000)
consumer.seek(TopicPartition(topic, 0), 0)

# Listen for new or old messages and push them to the Splunk index
logger.info('Consumer listen for topic ' + topic + '...')
while(True):
    try:
        eventPartition = consumer.poll(timeout_ms=200, max_records=1)
        if eventPartition:
            eventList = list(eventPartition.values())
            payload = eventList[0][0].value.decode('utf8')
            splunkIndex.submit(
                event=payload,
                sourcetype='kafka_stream'
            )
            logger.info(payload)
    except Exception as e:
        logger.error(e)