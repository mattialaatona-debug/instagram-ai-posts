import argparse
import json
import os
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "posts.json"
GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v23.0")
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


def load_state():
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_post(state, post_id=None, latest=False):
    posts = state["generated"]
    if latest:
        candidates = [post for post in posts if not post.get("published")]
        if not candidates:
            raise SystemExit("No generated unpublished posts found")
        return candidates[-1]
    for post in posts:
        if post["id"] == post_id:
            return post
    raise SystemExit(f"Generated post not found: {post_id}")


def graph_post(path, data):
    response = requests.post(f"{GRAPH_BASE}/{path}", data=data, timeout=60)
    if not response.ok:
        raise SystemExit(f"Meta API error {response.status_code}: {response.text}")
    return response.json()


def notify_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text},
        timeout=30,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id")
    parser.add_argument("--latest", action="store_true")
    args = parser.parse_args()

    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]
    state = load_state()
    post = select_post(state, args.post_id, args.latest)

    container = graph_post(
        f"{ig_user_id}/media",
        {
            "image_url": post["image_url"],
            "caption": post["caption"],
            "access_token": access_token,
        },
    )

    # Meta may need a short delay before the creation id is publishable.
    time.sleep(15)

    publish = graph_post(
        f"{ig_user_id}/media_publish",
        {
            "creation_id": container["id"],
            "access_token": access_token,
        },
    )

    notify_telegram(f"Published Instagram post {post['id']}: {publish.get('id')}")
    print(json.dumps({"post_id": post["id"], "instagram_media_id": publish.get("id")}, indent=2))


if __name__ == "__main__":
    main()

