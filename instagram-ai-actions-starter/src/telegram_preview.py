import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "posts.json"


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    with STATE_PATH.open("r", encoding="utf-8") as f:
        post = json.load(f)["generated"][-1]

    caption = (
        f"Instagram draft: {post['id']}\n\n"
        f"{post['caption']}\n\n"
        f"Image: {post['image_url']}\n\n"
        "To publish manually: Actions -> Publish approved Instagram post -> "
        f"post_id={post['id']}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data={"chat_id": chat_id, "photo": post["image_url"], "caption": caption[:1024]},
        timeout=60,
    )
    if not response.ok:
        raise SystemExit(f"Telegram error {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()

