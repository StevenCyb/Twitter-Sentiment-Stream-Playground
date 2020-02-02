const request = require("request")
var NodeTweetStream = require("node-tweet-stream")

// Parse the env variables
console.log("Initialization...");
const { 
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN_KEY,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_LANGUAGE,
    TWITTER_TRACKS,
    SAS_PROXY_HOST
} = process.env;
const consumerKey = process.env.TWITTER_CONSUMER_KEY || "";
const consumerSecret = process.env.TWITTER_CONSUMER_SECRET || "";
const accessTokenKey = process.env.TWITTER_ACCESS_TOKEN_KEY || "";
const accessTokenSecret = process.env.TWITTER_ACCESS_TOKEN_SECRET || "";
const language = process.env.TWITTER_LANGUAGE || "en";
const tracks = (process.env.TWITTER_TRACKS || "").split(",");
const proxy = process.env.SAS_PROXY_HOST || "sioproxy:80";

// Connect to Twitter
console.log("Connecting tweet stream...");
nodeTweetStream = new NodeTweetStream({
    consumer_key: consumerKey,
    consumer_secret: consumerSecret,
    token: accessTokenKey,
    token_secret: accessTokenSecret
});

// Add an error event
nodeTweetStream.on("error", function (err) {
    console.log("Twitter Error", err);
});

// Create a string of tracks
var tracksString = "";
tracks.forEach(track => tracksString += (track + "_"));
tracksString = tracksString.substr(0, tracksString.length - 1)
// Add a tweet event
nodeTweetStream.on("tweet", function (tweet) {
    // Check for language since sentiment is trained on english examples
    if(language == tweet.lang) {
        // Create a payload (JSON-Object)
        var payload = {
            "location": tweet.user.location,
            "geo": tweet.geo,
            "tracks": tracksString,
            "hashtags": tweet.entities.hashtags,
            "created_at": tweet.created_at,
            "reply_count": tweet.reply_count, 
            "retweet_count": tweet.retweet_count, 
            "text": (("extended_tweet" in tweet && "full_text" in tweet.extended_tweet)?tweet.extended_tweet.full_text: tweet.text).replace(/[^a-zA-Z# 0-9.,]{0,}(\r\n|\r|\n){0,}/g, "")
        };
        // Push the payload to Nginx (than to one of the available SAS)
        request.post("http://" + proxy, {
                json: payload
        }, (error, res, body) => {
            console.log("Tweet", " - ", "Forward" + ((error == null)?"[SUCCEEDED]":"[FAILED]"), ":\r\n",  payload);
        });
    }
});

// Add tracks
console.log("Track: ", tracks);
tracks.forEach(track => nodeTweetStream.track(track));