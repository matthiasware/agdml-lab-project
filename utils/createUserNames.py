import qrcode
import random
import binascii
import os
import csv
import argparse


def genUser():
    return binascii.b2a_hex(os.urandom(15)).decode('ascii')


def genHaikuNick():
    adjs = ["autumn", "hidden", "bitter", "misty", "silent",
            "empty", "dry", "dark", "summer", "icy",
            "delicate", "quiet", "white", "cool", "spring",
            "winter", "patient", "twilight", "dawn", "crimson",
            "wispy", "weathered", "blue", "billowing", "broken",
            "cold", "damp", "falling", "frosty", "green",
            "long", "late", "lingering", "bold", "little",
            "morning", "muddy", "old", "red", "rough", "still",
            "small", "sparkling", "throbbing", "shy", "wandering",
            "withered", "wild", "black", "young", "holy", "solitary",
            "fragrant", "aged", "snowy", "proud", "floral", "restless",
            "divine", "polished", "ancient", "purple", "lively", "nameless"
            ]
    nouns = ["waterfall", "river", "breeze", "moon", "rain", "wind", "sea",
             "morning", "snow", "lake", "sunset", "pine", "shadow", "leaf",
             "dawn", "glitter", "forest", "hill", "cloud", "meadow", "sun",
             "glade", "bird", "brook", "butterfly", "bush", "dew", "dust",
             "field", "fire", "flower", "firefly", "feather", "grass",
             "haze", "mountain", "night", "pond", "darkness", "snowflake",
             "silence", "sound", "sky", "shape", "surf", "thunder",
             "violet", "water", "wildflower", "wave", "water", "resonance",
             "sun", "wood", "dream", "cherry", "tree", "fog", "frost",
             "voice", "paper", "frog", "smoke", "star"
             ]
    return (random.choice(adjs) +
            "-" + random.choice(adjs) +
            "-" + random.choice(nouns) +
            "-" + random.choice(nouns))


def create(nusers, dir_data="users", file_users="users.csv"):
    user_nicks = [(genUser(), genHaikuNick()) for i in range(nusers)]
    users = [(qrcode.make("user:'{}' nick:{}".format(user, nick)), user, nick)
             for user, nick in user_nicks]

    for img, user, nick in users:
        img.save(os.path.join(dir_data, "{}::{}.png".format(user, nick)),
                 "PNG")

    with open(os.path.join(dir_data, file_users), "w") as file:
        writer = csv.writer(file)
        writer.writerows(user_nicks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create users (user-id, nick) csv file + qr codes')
    parser.add_argument('n', type=int, help='number of users')
    args = parser.parse_args()
    create(args.n)
