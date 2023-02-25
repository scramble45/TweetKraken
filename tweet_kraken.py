import os
import random
import time
import requests
import re
import emoji
import tweepy
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from liquidctl import find_liquidctl_devices
from liquidctl.driver.kraken3 import KrakenZ3
import toml

# Load Twitter configuration from config.toml
config = toml.load("config.toml")

# Get Twitter API keys
consumer_key = config["twitter"]["consumer_key"]
consumer_secret = config["twitter"]["consumer_secret"]
access_token = config["twitter"]["access_token"]
access_token_secret = config["twitter"]["access_secret"]
usernames = config["twitter"]["usernames"]

# Configurables
no_tweet_counter = 0
interval = 1  # in minutes
randomize = True  # randomizes the array of search_tweets
max_no_tweets = 10  # If you try to search and no tweets for 10 attempts fail

# Set up the Tweepy API client
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Set up the Kraken Z3 device
devices = find_liquidctl_devices()
dev = next(
    (device for device in devices if "NZXT Kraken Z" in device.description), None
)

if dev is None:
    print("No Kraken Z3 device found")
else:
    print(f"Kraken Z3 device found: {dev.description}")
    # Connect to Kraken
    kraken_image = dev.connect()

    print("- initialize")
    init_status = dev.initialize()

    # Print all data returned by `initialize`.
    if init_status:
        for key, value, unit in init_status:
            print(f"- {key}: {value} {unit}")

    while True:
        # Randomize the order of the search queries if requested
        if randomize:
            random.shuffle(usernames)

        for username in usernames:
            print(f"Searching for twitter timeline for: @{username}")

            # Get the user's timeline
            timeline = api.user_timeline(screen_name=username, count=1)

            if not timeline:
                # If the user has no tweets in their timeline, increment the no_tweet_counter
                no_tweet_counter += 1

                # If the no_tweet_counter reaches 10, break out of the loop
                if no_tweet_counter >= max_no_tweets:
                    break

                print(f"No tweets found for user {username}")
                continue

            # Reset the no_tweet_counter if a user with tweets is found
            no_tweet_counter = 0

            latest_tweet = timeline[0]
            tweet_author = latest_tweet.author.name
            tweet_text = latest_tweet.text

            # Replace the avatar image with the tweet image if it exists
            avatar_url = latest_tweet.author.profile_image_url_https.replace(
                "_normal", "_400x400"
            )
            tweet_entities = latest_tweet.entities
            if (
                "media" in tweet_entities
                and tweet_entities["media"][0]["type"] == "photo"
            ):
                avatar_url = tweet_entities["media"][0]["media_url_https"]

            print(f"avatar_url: {avatar_url}")

            # Download the avatar or tweet image and resize it to fit within the Kraken screen
            avatar_data = requests.get(avatar_url)  # .content

            # If the tweet contains an image, use that image in place of the avatar_image
            if (
                "media" in tweet_entities
                and tweet_entities["media"][0]["type"] == "photo"
            ):
                avatar_data = requests.get(
                    tweet_entities["media"][0]["media_url_https"]
                ).content
                avatar_image = Image.open(BytesIO(avatar_data))
                if avatar_image.mode != "RGB":
                    avatar_image = avatar_image.convert("RGB")
                crop_size = (250, 250)
                if avatar_image.size != crop_size:
                    # Crop the center of the image to fit the target size
                    width, height = avatar_image.size
                    left = (width - crop_size[0]) / 2
                    top = (height - crop_size[1]) / 2
                    right = left + crop_size[0]
                    bottom = top + crop_size[1]
                    avatar_image = avatar_image.crop((left, top, right, bottom))
            else:
                avatar_image = Image.new("RGB", (250, 250), "black")
                avatar_image_data = requests.get(avatar_url).content
                avatar_image_data = re.sub(b"_normal(?=\.png)", b"", avatar_image_data)
                avatar_image = Image.open(BytesIO(avatar_image_data))
                avatar_image = avatar_image.convert("RGB")
                avatar_size = (250, 250)
                if avatar_image.size != avatar_size:
                    avatar_image = avatar_image.resize(avatar_size)

            gif_frame = Image.new("RGB", (250, 250), "black")

            # Paste the avatar image in the center of the image
            avatar_left = (gif_frame.width - avatar_image.width) // 2
            avatar_top = (gif_frame.height - avatar_image.height) // 2
            gif_frame.paste(avatar_image, (avatar_left, avatar_top))

            # Add the tweet text in the center of the image
            font_size = 20
            font = ImageFont.truetype("chirp-medium-web.ttf", font_size)

            # Strip links from the tweet text and replace emojis with their descriptions
            tweet_text = re.sub(r"http\S+", "", tweet_text)
            emoji_chars = [
                chr(codepoint)
                for codepoint in emoji.EMOJI_DATA.keys()
                if "category" in emoji.EMOJI_DATA[codepoint]
                and emoji.EMOJI_DATA[codepoint]["category"] != "Text"
            ]
            tweet_text = "".join(
                c for c in tweet_text if c.isascii() or c in emoji_chars
            )

            tweet_text = emoji.demojize(tweet_text)

            # Split the tweet text into lines to fit within the center of the image
            max_lines = 6
            text_max_width = gif_frame.width - 30
            words = tweet_text.split()
            lines = []
            line = ""
            for word in words:
                if font.getlength(line + " " + word) < text_max_width:
                    line += " " + word
                else:
                    # If the word doesn't fit, split the line and start a new one
                    if len(line) == 0:
                        line = word
                    lines.append(line.strip())
                    line = word

            if len(line) > 0:
                lines.append(line.strip())

            # Wrap the last word if it's a single word and doesn't fit
            if len(lines) > 0:
                last_line = lines[-1]
                if (
                    len(last_line.split()) == 1
                    and font.getlength(last_line) > text_max_width
                ):
                    lines[-2] += " " + last_line
                    lines.pop()

            # Truncate the text with ellipsis if it's too long to fit in the center of the image
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                last_line = lines[-1]

                if len(last_line) > 3:
                    lines[-1] = last_line[: len(last_line) - 3] + "..."

            # Calculate the text size and position to center it in the image
            if lines:
                text_width = max(font.getlength(line) for line in lines)
                text_bbox = font.getbbox(" ".join(lines))
                text_height = (
                    text_bbox[3] - text_bbox[1] + (len(lines) - 1) * font.getlength("X")
                )

                text_x = (gif_frame.width - text_width) // 2 + 4
                text_y = (gif_frame.height - text_height) // 2

                # Add a white shadow behind the text for better visibility
                shadow_offset = 2
                shadow_draw = ImageDraw.Draw(gif_frame)
                for i, line in enumerate(lines):
                    line_bbox = font.getbbox(line)
                    line_height = line_bbox[3] - line_bbox[1]
                    if text_y + line_height > gif_frame.height:
                        break
                    shadow_draw.text(
                        (text_x - shadow_offset, text_y), line, font=font, fill="white"
                    )
                    shadow_draw.text(
                        (text_x + shadow_offset, text_y), line, font=font, fill="white"
                    )
                    shadow_draw.text(
                        (text_x, text_y - shadow_offset), line, font=font, fill="white"
                    )
                    shadow_draw.text(
                        (text_x, text_y + shadow_offset), line, font=font, fill="white"
                    )
                    text_y += line_height

                # Add the tweet text in black
                text_draw = ImageDraw.Draw(gif_frame)
                text_y = (gif_frame.height - text_height) // 2
                for i, line in enumerate(lines):
                    line_bbox = font.getbbox(line)
                    line_height = line_bbox[3] - line_bbox[1]
                    if text_y + line_height > gif_frame.height:
                        break
                    text_draw.text((text_x, text_y), line, font=font, fill="black")
                    text_y += line_height

            # Save the GIF image to disk and display it on the Kraken Z3 screen
            gif_frame.save("tweet.gif", quality=100)

            kraken_image.set_screen(
                "lcd",
                "gif",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "tweet.gif"),
            )
            print(f'Tweet displayed: "{tweet_text}"')

            # Wait for the specified interval before displaying the next tweet
            time.sleep(interval * 60)
