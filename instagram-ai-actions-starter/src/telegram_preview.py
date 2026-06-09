import argparse
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "posts.json"


def load_post(post_id=None):
    with STATE_PATH.open("r", encoding="utf-8") as f:
        posts = json.load(f)["generated"]

    if not posts:
        raise SystemExit("No generated posts found")

    if post_id:
        for post in posts:
            if post["id"] == post_id:
                return post
        raise SystemExit(f"Post not found: {post_id}")

    return posts[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", default="")
    args = parser.parse_args()

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    post = load_post(args.post_id.strip() or None)

    caption = f"Instagram image ready: {post['id']}\n\nTopic: {post.get('topic', '')}"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "Open Instagram", "url": "https://www.instagram.com/"},
                {"text": "Download Image", "url": post["image_url"]},
            ]
        ]
    }

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={
            "chat_id": chat_id,
            "photo": post["image_url"],
            "caption": caption[:1024],
            "reply_markup": json.dumps(reply_markup),
        },
        timeout=60,
    )
    if not response.ok:
        raise SystemExit(f"Telegram error {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()
