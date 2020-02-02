# Twitter-Sentiment-Stream-Playground
A simple playground for evaluating Twitter data within Docker and with the help of Tensorflow and Splunk. *This is not a sample solution, but rather a playground to play with Tensorflow within Docker, Kafka and Splunk.*

The picture below illustrates the structure of the cluster. There can be up to two Twitter Stream Service (TSS) under one IP. These send the tweets to Nginx. Nginx itself distributes the tweets to the available Sentiment Analysis Service (SAS). In this service the sentiment value is added to the JSON-object and sent to Kafka. Kafka2Splunk Service (K2SS) take the messages from Kafka and send them to Splunk.
![Overview](/media/overview.jpg)

You can run the cluster with `sh run_compose.sh` and stop with `sh stop_compose.sh`. To completely reset the Docker, use `sh reset_docker.sh` (delete everything). Just play around with it a little ;)

K2SS creat a index automatically.You can use the dashboard template from the repository to quickly and easily visualize the data.
![Overview-Splunk](/media/splunk.jpg)
