# TweetKraken

### Display some tweets your AIO because why not.

**TweetKraken** is a Python script that displays tweets on the NZXT Kraken Z liquid cooler LCD screen. It connects to the Twitter API and downloads the latest tweet from a list of specified usernames. The script then generates an image with the tweet text and the user's profile picture, and displays it on the Kraken Z LCD screen, or if the user attaches an image to the tweet it uses that.

To use TweetKraken, you will need to create a Twitter Developer account and obtain API keys and access tokens. Once you have your credentials, rename the .env.sample file to .env and replace the placeholders with your actual Twitter API credentials and the list of usernames you want to follow.

### Usage

1. Install the required dependencies by running pip install -r requirements.txt.
2. Rename the .env.sample file to .env and replace the placeholders with your Twitter API credentials and the list of usernames you want to follow.
3. Connect the NZXT Kraken Z3 device to your computer.
4. Run the script by running python tweet_kraken.py.
5. The script will display the latest tweet from the specified list of usernames on the Kraken Z3 screen. It will continue to update the screen with the latest tweets at the specified interval.

**Note:** Make sure to modify the .env file by including your Twitter API credentials and making any necessary changes to the list of usernames that TweetKraken loads. This has only been tested on Linux there may be dragons in M$ Windows land. PRs are welcome.
