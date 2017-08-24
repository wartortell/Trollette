import os
import tweepy
import argparse

from helpers import default_logger


class TwitterAPI:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.twitter_auth = None

        try:
            import configparser
            parser = configparser.ConfigParser()
            conf_path = os.environ.get("TROLLETTE_CONFIG", "~/.config/trollette")
            parser.read(os.path.expanduser(conf_path))

            self.twitter_api = {"consumer_key": parser.get("twitter", "consumer_key"),
                                "consumer_secret": parser.get("twitter", "consumer_secret"),
                                "access_token": parser.get("twitter", "access_token"),
                                "access_token_secret": parser.get("twitter", "access_token_secret")}
        except:
            self.api = ""

            self.twitter_api = {"consumer_key": "",
                                "consumer_secret": "",
                                "access_token": "",
                                "access_token_secret": ""}

    def auth_twitter(self):
        if not self.twitter_auth:

            self.logger("Authorizing Twitter...")
            auth = tweepy.OAuthHandler(self.twitter_api["consumer_key"], self.twitter_api["consumer_secret"])
            auth.secure = True
            auth.set_access_token(self.twitter_api["access_token"], self.twitter_api["access_token_secret"])

            self.twitter_auth = tweepy.API(auth)

            self.logger("  Twitter API Auth Success: %s" % self.twitter_auth.me().name)

    def farm_tweets(self, topic, count=100):
        self.auth_twitter()

        r = self.twitter_auth.search(q=topic, count=count)

        tweets = []
        for tweet in r:
            tweets.append({"tweet": tweet.text, "author": tweet.author.name})

        return tweets

    def farm_users_twitter(self, screen_name, count=100):
        self.auth_twitter()

        user_tweets = self.twitter_auth.user_timeline(screen_name=screen_name, count=count)

        tweets = []
        for tweet in user_tweets:
            tweets.append(tweet.text)
        return tweets


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--term", action="store", required=False, help="Term to search twitter with")
    parser.add_argument("-u", "--user", action="store", required=False, help="Username to search twitter for")
    args = parser.parse_args()

    twit = TwitterAPI()
    if args.term:
        for tweet in twit.farm_tweets(args.term):
            print("{} -{}".format(tweet["tweet"], tweet["author"]))
    elif args.user:
        print("\n".join(twit.farm_users_twitter(args.user)))
    else:
        parser.print_help()

