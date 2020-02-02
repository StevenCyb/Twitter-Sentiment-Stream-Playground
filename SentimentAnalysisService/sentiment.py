import re
import sys
import logging
from os import path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
import numpy

class Sentiment:
    def __init__(self, logger):
        self.logger = logger
        self.wordIndex = None
        # Create model
        self.logger.info('Create model...')
        self.model = keras.Sequential()
        self.model.add(Embedding(88000, 16))
        self.model.add(GlobalAveragePooling1D())
        self.model.add(Dense(16, activation="relu"))
        self.model.add(Dense(1, activation="sigmoid"))
        #self.model.summary()
        # Compile model
        self.logger.info('Compile model...')
        self.model.compile(optimizer="adam", loss="binary_crossentropy", metrics=['accuracy'])

    def train(self, weights='weights.h5', epochs=40, batchSize=512):
        # Loading modoel if exist
        if(path.isfile(weights)):
            self.loadWeights(weights)
        # Load data
        self.logger.info('Load data...')
        data = keras.datasets.imdb
        (trainData, trainLabels), (testData, testLabels) = data.load_data(num_words=10000)
        # Encode data
        self.logger.info('Encode data...')
        self.wordIndex = data.get_word_index() 
        self.wordIndex = {k:(v+3) for k, v in self.wordIndex.items()}
        self.wordIndex["<PAD>"] = 0
        self.wordIndex["<START>"] = 1
        self.wordIndex["<UNK>"] = 2
        self.wordIndex["<UNUSED>"] = 3
        # Preprocess data
        self.logger.info('Preprocess data...')
        trainData = keras.preprocessing.sequence.pad_sequences(trainData, value=self.wordIndex["<PAD>"], padding="post", maxlen=250)
        testData = keras.preprocessing.sequence.pad_sequences(testData, value=self.wordIndex["<PAD>"], padding="post", maxlen=250)
        # Split train- and validation data
        self.logger.info('Split data into train and validation...')
        xVal = trainData[:10000]
        xTrain = trainData[10000:]
        yVal = trainLabels[:10000]
        yTrain = trainLabels[10000:]
        # Training the model
        self.logger.info('Start training with bs=' + str(batchSize) + ' and epochs=' + str(epochs) + "...")
        fitModel = self.model.fit(xTrain, yTrain, epochs=epochs, batch_size=batchSize, validation_data=(xVal, yVal), verbose=1)
        # Testing the model
        self.logger.info('Run evaluation...')
        results = self.model.evaluate(testData, testLabels)
        self.logger.info('Evaluation results: ' + str(results))
        # Saving model
        self.logger.info('Save model at ' + weights)
        self.model.save(weights)

    def loadWeights(self, weights='weights.h5'):
        self.logger.info('Load weights from ' + weights + '...')
        self.model = keras.models.load_model(weights)

    def loadWordIndex(self):
        # Load the word index of Keras
        self.logger.info('Load word index...')
        self.wordIndex = keras.datasets.imdb.get_word_index() 
        self.wordIndex = {k:(v+3) for k, v in self.wordIndex.items()}
        self.wordIndex["<PAD>"] = 0
        self.wordIndex["<START>"] = 1
        self.wordIndex["<UNK>"] = 2
        self.wordIndex["<UNUSED>"] = 3

    def predict(self, text):
        # Encode
        text = text.encode('utf-8')
        # Preprocess text
        if type(text) == bytes:
            text = text.decode('utf-8')
        text = re.sub(r'(\.|,|\(|\)|!|;|:|_|-|#|"|\[|\]|\\|\/)', ' ', text)
        encoded = [1]
        for word in text.split():
            if word.lower() in self.wordIndex:
                encoded.append(self.wordIndex[word.lower()])
            else:
                encoded.append(2)
        encoded = keras.preprocessing.sequence.pad_sequences([encoded], value=self.wordIndex["<PAD>"], padding="post", maxlen=250)
        # Run prediction and return prediction
        predict = self.model.predict(encoded)
        return predict[0].item()

if __name__ == '__main__':
    # Some logic for prompt - Read the last logs
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    sentiment = Sentiment(logger)
    if len(sys.argv) == 2 and sys.argv[1] == '-t':
        if len(sys.argv) == 2:
            sentiment.train()
        elif len(sys.argv) == 3:
            sentiment.train(weights=sys.argv[2])
        elif len(sys.argv) == 4:
            sentiment.train(weights=sys.argv[2], epochs=sys.argv[3])
        elif len(sys.argv) == 5:
            sentiment.train(weights=sys.argv[2], epochs=int(sys.argv[3]), batch_size=int(sys.argv[4]))
        else:
            logger.info('Unknown argument constalation:')
            logger.info(sys.argv)
    elif len(sys.argv) == 3 and sys.argv[1] == '-s':
        logger.info('Load weights...')
        sentiment.loadWordIndex()
        sentiment.loadWeights()
        logger.info('Analysis sentiment of "' + sys.argv[2] + '": ' + str(sentiment.predict(sys.argv[2])))
    elif len(sys.argv) == 4 and sys.argv[1] == '-s':
        logger.info('Load weights...')
        sentiment.loadWordIndex()
        sentiment.loadWeights(sys.argv[2])
        logger.info('Analysis sentiment of "' + sys.argv[3] + '": ' + str(sentiment.predict(sys.argv[3])))
    else:
        logger.info('You can use:')
        logger.info('-t => Train with Movie Reviews Sentiment Classification dataset (IMDB). Weights saved under weights.h5.')
        logger.info('-t name.h5 => Train with Movie Reviews Sentiment Classification dataset (IMDB). Weights saved under name.h5.')
        logger.info('-t name.h5 40 => Train with Movie Reviews Sentiment Classification dataset (IMDB). Train 40 epochs and save weights under name.h5.')
        logger.info('-t name.h5 40 512 => Train with Movie Reviews Sentiment Classification dataset (IMDB). Train 40 epochs with batch-size of 512 and save weights under name.h5.')
        logger.info('-s weights.h5 "Some text to analyze." => To perform a sentiment analysis.')
