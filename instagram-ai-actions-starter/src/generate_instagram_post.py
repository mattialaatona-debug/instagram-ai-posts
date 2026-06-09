import argparse
import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "content" / "queue.yml"
STATE_PATH = ROOT / "state" / "posts.json"
OUTPUT_DIR = ROOT / "public" / "generated"


def load_queue():
    with QUEUE_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)["posts"]


def load_state():
    if not STATE_PATH.exists():
        return {"generated": []}
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def choose_post(posts, state, post_id=None):
    if post_id:
        for post in posts:
            if post["id"] == post_id:
                return post
        raise SystemExit(f"Unknown post_id: {post_id}")

    generated_ids = {item["id"] for item in state["generated"]}
    for post in posts:
        if post["id"] not in generated_ids:
            return post
    raise SystemExit("No unpublished prompts left in content/queue.yml")


def generate_image(post):
    client = OpenAI()
    style = os.getenv("BRAND_STYLE", "")
    model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    prompt = f"{post['prompt']}\n\nBrand style: {style}\nFormat: square Instagram feed post, polished, no small text."

    result = client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024",
        quality="low",
        n=1,
    )
    image_b64 = result.data[0].b64_json
    return base64.b64decode(image_b64)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-id", default="")
    args = parser.parse_args()

    posts = load_queue()
    state = load_state()
    post = choose_post(posts, state, args.post_id.strip() or None)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image_bytes = generate_image(post)
    image_path = OUTPUT_DIR / f"{post['id']}.png"
    caption_path = OUTPUT_DIR / f"{post['id']}.txt"

    image_path.write_bytes(image_bytes)
    caption_path.write_text(post["caption"].strip() + "\n", encoding="utf-8")

    public_base = os.environ["PUBLIC_ASSET_BASE_URL"].rstrip("/")
    record = {
        "id": post["id"],
        "topic": post.get("topic", ""),
        "image_path": str(image_path.relative_to(ROOT)).replace("\\", "/"),
        "caption_path": str(caption_path.relative_to(ROOT)).replace("\\", "/"),
        "image_url": f"{public_base}/{post['id']}.png",
        "caption": post["caption"].strip(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "published": False,
    }

    state["generated"] = [item for item in state["generated"] if item["id"] != post["id"]]
    state["generated"].append(record)
    save_state(state)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

