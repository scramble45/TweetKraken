# TweetKraken

<p align="center">
  <img src="./images/tweet_kraken.png" alt="TweetKraken"/>
</p>

### Display some tweets on your AIO because why not.

**TweetKraken** is a Python script that displays tweets on the NZXT Kraken Z liquid cooler LCD screen. It connects to the Twitter API and downloads the latest tweet from a list of specified usernames. The script then generates an image with the tweet text and the user's profile picture, and displays it on the Kraken Z LCD screen, or if the user attaches an image to the tweet it uses that.

To use TweetKraken, you will need to create a [Twitter Developer](https://developer.twitter.com/) account and obtain API keys and access tokens. Once you have your credentials, copy the `config.toml.sample` file to `config.toml` and replace the placeholders with your actual Twitter API credentials and the list of usernames you want to follow.

### Usage

1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Copy the `config.toml.sample` file to `config.toml` and replace the placeholders with your Twitter API credentials and the list of usernames you want to follow.
3. Connect the NZXT Kraken Z3 device to your computer USB header.
4. Run the script by running `python tweet_kraken.py`.
5. The script will display the latest tweet from the specified list of usernames on the Kraken Z3 screen. It will continue to update the screen with the latest tweets at the specified interval.
6. Setup a systemd service to background it.

**Note:** Make sure to modify the `config.toml` file by including your [Twitter API credentials](https://developer.twitter.com/) and making any necessary changes to the list of usernames that TweetKraken loads. This has only been tested on Linux there may be dragons in M$ Windows land. PRs are welcome.
