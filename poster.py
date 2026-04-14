#!/usr/bin/env python3
"""
Dr Liew Social Media Auto-Poster
─────────────────────────────────
Reads today's posts from the embedded post data and publishes to:
  • Facebook Page          (Meta Graph API)
  • Instagram Business     (Meta Graph API – two-step container publish)
  • LinkedIn Company Page  (LinkedIn REST API v2)

Images are read from the 'images/' subfolder, named YYYY-MM-DD-platform[-slideN].jpg
Carousels are posted as multi-image posts where supported.

Usage:
  python poster.py                  # posts today's content
  python poster.py --date 2026-05-07  # posts a specific date (for testing)
  python poster.py --dry-run        # shows what would be posted without posting
"""

import os, sys, json, time, logging, argparse, re
from datetime import date, datetime
from pathlib import Path

import requests

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("poster")

# ── Unicode helper ────────────────────────────────────────────────────────────────────────────────────
def fix_surrogates(text: str) -> str:
    """Convert surrogate pairs to proper Unicode characters.
    posts_data.py stores emoji as UTF-16 surrogate pairs (e.g. \\ud83e\\uddb4).
    Python 3's utf-8 encoder rejects lone surrogates, so we round-trip through
    utf-16 to merge the pairs into proper code points first."""
    try:
        return text.encode("utf-16", "surrogatepass").decode("utf-16")
    except Exception:
        return text.encode("utf-8", "surrogatepass").decode("utf-8", "replace")

# ── Configuration (from environment variables / GitHub Secrets) ────────────────
def env(key, required=True):
    val = os.environ.get(key, "").strip()
    if required and not val:
        log.error(f"Missing required environment variable: {key}")
        sys.exit(1)
    return val

# ── Post data import ───────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from posts_data2 import POSTS
except ImportError:
    try:
        from posts_data import POSTS
    except ImportError:
        log.error("Cannot import POSTS from posts_data.py or posts_data2.py")
        sys.exit(1)

# ── Image helpers ──────────────────────────────────────────────────────────────
IMAGES_DIR = Path(__file__).parent / "images"

def find_images(post: dict) -> list[Path]:
    """
    Returns list of image Paths for a post.
    Single posts: [YYYY-MM-DD-platform.jpg]
    Carousels:    [YYYY-MM-DD-platform-slide1.jpg, ..., -slideN.jpg]
    Falls back to any matching date+platform file if slides not found.
    """
    d     = post["date"]
    plat  = post["platform"].lower()
    fmt   = post.get("format", "").lower()

    if "carousel" in fmt:
        slides = sorted(IMAGES_DIR.glob(f"{d}-{plat}-slide*.jpg"))
        if not slides:
            slides = sorted(IMAGES_DIR.glob(f"{d}-{plat}-slide*.png"))
        if slides:
            return slides
        log.warning(f"No carousel slide images found for post {post['id']} — falling back to single image")

    # single image
    for ext in ("jpg", "jpeg", "png"):
        p = IMAGES_DIR / f"{d}-{plat}.{ext}"
        if p.exists():
            return [p]
    log.warning(f"No image found for post {post['id']} ({d}-{plat})")
    return []


# ── Image upload for Instagram (needs a public URL) ────────────────────────────
# Uses jsDelivr CDN to serve GitHub-hosted images with proper content-type headers.
# Instagram's API rejects raw.githubusercontent.com URLs; jsDelivr works reliably.
# Format: https://cdn.jsdelivr.net/gh/{owner}/{repo}@main/images/{filename}
def upload_image_for_instagram(image_path: Path) -> str:
    """Return a publicly accessible URL for an image already committed to the repo."""
    github_repo  = env("GITHUB_REPOSITORY")   # e.g. "drliewhipknee/dr-liew-social-media"
    filename     = image_path.name
    url = f"https://cdn.jsdelivr.net/gh/{github_repo}@main/images/{filename}"
    log.info(f"  jsDelivr CDN image URL: {url}")
    return url


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK
# ══════════════════════════════════════════════════════════════════════════════

def post_facebook(post: dict, images: list[Path], dry_run: bool) -> str | None:
    """Post to Facebook Page. Returns post ID on success."""
    page_id    = env("FB_PAGE_ID")
    page_token = env("FB_PAGE_ACCESS_TOKEN")
    caption    = fix_surrogates(post["caption"])
    if post.get("hashtags") and post["hashtags"] not in caption:
        caption += "\n\n" + post["hashtags"]
    if post.get("website_link"):
        caption += f"\n\n{post['website_link']}"

    if dry_run:
        log.info(f"  [DRY RUN] Facebook — would post: {post['topic'][:60]}")
        return "dry-run-fb"

    base = f"https://graph.facebook.com/v21.0/{page_id}"

    github_repo = env("GITHUB_REPOSITORY")

    def cdn_url(img_path: Path) -> str:
        return f"https://cdn.jsdelivr.net/gh/{github_repo}@main/images/{img_path.name}"

    if len(images) > 1:
        # Carousel: upload each image via URL as unpublished, then post to feed
        media_ids = []
        for img in images:
            r = requests.post(
                f"{base}/photos",
                data={"access_token": page_token, "published": "false", "url": cdn_url(img)},
                timeout=60,
            )
            r.raise_for_status()
            media_ids.append(r.json()["id"])
            time.sleep(1)

        attached = {f"attached_media[{i}]": json.dumps({"media_fbid": mid}) for i, mid in enumerate(media_ids)}
        r = requests.post(
            f"{base}/feed",
            data={"message": caption, "access_token": page_token, **attached},
            timeout=30,
        )
    elif images:
        # Single image: upload unpublished via JSON, then publish via /feed
        r = requests.post(
            f"{base}/photos",
            json={"access_token": page_token, "published": False, "url": cdn_url(images[0])},
            timeout=60,
        )
        r.raise_for_status()
        photo_id = r.json()["id"]
        r = requests.post(
            f"{base}/feed",
            json={
                "message": caption,
                "access_token": page_token,
                "attached_media": [{"media_fbid": photo_id}],
            },
            timeout=30,
        )
    else:
        r = requests.post(
            f"{base}/feed",
            data={"message": caption, "access_token": page_token},
            timeout=30,
        )

    r.raise_for_status()
    post_id = r.json().get("post_id") or r.json().get("id")
    log.info(f"  Facebook OK  → post ID: {post_id}")
    return post_id


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM
# ══════════════════════════════════════════════════════════════════════════════

def post_instagram(post: dict, images: list[Path], dry_run: bool) -> str | None:
    """Post to Instagram Business Account. Returns post ID."""
    ig_id      = env("IG_BUSINESS_ACCOUNT_ID")
    page_token = env("FB_PAGE_ACCESS_TOKEN")
    caption    = fix_surrogates(post["caption"])
    if post.get("hashtags") and post["hashtags"] not in caption:
        caption += "\n\n" + post["hashtags"]

    if dry_run:
        log.info(f"  [DRY RUN] Instagram — would post: {post['topic'][:60]}")
        return "dry-run-ig"

    base = f"https://graph.facebook.com/v19.0/{ig_id}"

    if len(images) > 1:
        # Carousel: create item containers, then carousel container
        item_ids = []
        for img in images:
            img_url = upload_image_for_instagram(img)
            r = requests.post(
                f"{base}/media",
                data={
                    "image_url":    img_url,
                    "is_carousel_item": "true",
                    "access_token": page_token,
                },
                timeout=30,
            )
            r.raise_for_status()
            item_ids.append(r.json()["id"])
            time.sleep(1)

        r = requests.post(
            f"{base}/media",
            data={
                "media_type":    "CAROUSEL",
                "caption":       caption,
                "children":      ",".join(item_ids),
                "access_token":  page_token,
            },
            timeout=30,
        )
        r.raise_for_status()
        container_id = r.json()["id"]

    elif images:
        img_url = upload_image_for_instagram(images[0])
        r = requests.post(
            f"{base}/media",
            data={"image_url": img_url, "caption": caption, "access_token": page_token},
            timeout=30,
        )
        r.raise_for_status()
        container_id = r.json()["id"]
    else:
        log.warning("  Instagram: no image — skipping (Instagram requires an image)")
        return None

    # Poll until container is ready
    for attempt in range(12):
        time.sleep(5)
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{container_id}",
            params={"fields": "status_code", "access_token": page_token},
            timeout=15,
        )
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            break
        if status == "ERROR":
            log.error(f"  Instagram container error for post {post['id']}")
            return None
        log.info(f"  Instagram container status: {status} (attempt {attempt+1})")
    else:
        log.error("  Instagram container did not finish in time")
        return None

    # Publish
    r = requests.post(
        f"{base}/media_publish",
        data={"creation_id": container_id, "access_token": page_token},
        timeout=30,
    )
    r.raise_for_status()
    post_id = r.json()["id"]
    log.info(f"  Instagram OK → post ID: {post_id}")
    return post_id


# ══════════════════════════════════════════════════════════════════════════════
# LINKEDIN  (new Posts API — /rest/posts, LinkedIn-Version 202401)
# ══════════════════════════════════════════════════════════════════════════════

LI_VERSION = "202603"


def _li_get_member_urn(token: str) -> str:
    """Call /v2/userinfo (OpenID Connect) to get the member's person URN.
    Returns urn:li:person:{sub} — compatible with the new /rest/posts API.
    Requires openid + profile scopes on the token.
    """
    r = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    log.info(f"  /v2/userinfo → {r.status_code} {r.text[:300]}")
    r.raise_for_status()
    sub = r.json().get("sub", "")
    urn = f"urn:li:person:{sub}"
    log.info(f"  Detected member URN: {urn}")
    return urn


def _li_upload_image_new(owner_urn: str, token: str, image_path: Path) -> str:
    """Upload image via LinkedIn's new Images API. Returns urn:li:image:..."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    # Step 1: initialise upload
    r = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": owner_urn}},
        timeout=15,
    )
    log.info(f"  initializeUpload → {r.status_code} {r.text[:200]}")
    r.raise_for_status()
    val = r.json().get("value", {})
    upload_url = val["uploadUrl"]
    image_urn  = val["image"]

    # Step 2: upload binary
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    up = requests.put(
        upload_url,
        data=img_bytes,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        timeout=60,
    )
    up.raise_for_status()
    log.info(f"  LinkedIn image uploaded (new API): {image_urn}")
    return image_urn


def _li_post_new(author_urn: str, token: str, caption: str, image_path: Path | None, dry_run: bool) -> str:
    """Post via LinkedIn's new Posts API (/rest/posts)."""
    if dry_run:
        log.info(f"  [DRY RUN] LinkedIn post to {author_urn}")
        return "dry-run-li"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LI_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    body: dict = {
        "author": author_urn,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    if image_path and image_path.exists():
        image_urn = _li_upload_image_new(author_urn, token, image_path)
        body["content"] = {"media": {"id": image_urn}}

    r = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json=body,
        timeout=30,
    )
    log.info(f"  /rest/posts → {r.status_code} {r.text[:300]}")
    r.raise_for_status()
    try:
        post_id = r.headers.get("x-restli-id") or r.json().get("id", "unknown")
    except Exception:
        post_id = "unknown"
    log.info(f"  LinkedIn OK  → {author_urn}  post ID: {post_id}")
    return post_id


def post_linkedin(post: dict, images: list[Path], dry_run: bool) -> dict:
    """
    Post to LinkedIn personal profile and optionally company page.
    Uses the new /rest/posts API (LinkedIn-Version 202401) with urn:li:person:{sub}.
    """
    token      = env("LI_ACCESS_TOKEN")
    company_id = env("LI_COMPANY_PAGE_ID", required=False)

    caption = fix_surrogates(post["caption"])
    if post.get("hashtags") and post["hashtags"] not in caption:
        caption += "\n\n" + post["hashtags"]
    if post.get("website_link"):
        caption += f"\n\n{post['website_link']}"

    audience = post.get("li_audience", "Both").lower()
    image    = images[0] if images else None
    results  = {}
    personal_failed = False

    if audience in ("both", "personal"):
        # Auto-detect the member URN via OpenID Connect /v2/userinfo
        member_urn = env("LI_PERSONAL_URN", required=False)
        try:
            member_urn = _li_get_member_urn(token)
        except Exception as e:
            log.warning(f"  /v2/userinfo unavailable ({e}); using LI_PERSONAL_URN={member_urn}")

        if member_urn:
            try:
                results["personal"] = _li_post_new(member_urn, token, caption, image, dry_run)
            except Exception as e:
                log.error(f"  Personal LinkedIn post failed: {e}")
                results["personal_error"] = str(e)
                personal_failed = True
        else:
            log.error("  No member URN available — skipping personal LinkedIn post")
            personal_failed = True

    if company_id and audience in ("both", "company"):
        company_urn = f"urn:li:organization:{company_id}"
        try:
            results["company"] = _li_post_new(company_urn, token, caption, image, dry_run)
        except Exception as e:
            log.error(f"  Company LinkedIn post failed: {e}")
            results["company_error"] = str(e)
            # Don't re-raise — company requires w_organization_social which may not be available

    if personal_failed and audience in ("both", "personal"):
        raise Exception(results.get("personal_error", "Personal LinkedIn post failed"))

    return results


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def get_todays_posts(target_date: str) -> list[dict]:
    return [p for p in POSTS if p["date"] == target_date]


def run(target_date: str, dry_run: bool, platform_filter: str = "all"):
    log.info(f"═══ Dr Liew Social Media Poster  |  date={target_date}  dry_run={dry_run}  platform={platform_filter} ═══")

    posts = get_todays_posts(target_date)
    if platform_filter != "all":
        posts = [p for p in posts if platform_filter.lower() in p["platform"].lower()]
    if not posts:
        log.info(f"No posts scheduled for {target_date} — nothing to do.")
        return

    log.info(f"Found {len(posts)} post(s) for {target_date}")
    results = []

    for post in posts:
        log.info(f"\n── Post #{post['id']}  [{post['platform']}]  {post['topic']}")
        images = find_images(post)
        log.info(f"   Images found: {[str(i.name) for i in images] or 'none'}")

        platform = post["platform"].lower()
        post_results = {"post_id": post["id"], "date": post["date"],
                        "platform": post["platform"], "topic": post["topic"]}

        try:
            if "instagram" in platform:
                post_results["ig_post_id"] = post_instagram(post, images, dry_run)

            elif "facebook" in platform:
                post_results["fb_post_id"] = post_facebook(post, images, dry_run)

            elif "linkedin" in platform:
                li = post_linkedin(post, images, dry_run)
                post_results.update(li)

            post_results["status"]    = "posted"
            post_results["posted_at"] = datetime.utcnow().isoformat() + "Z"

        except requests.HTTPError as e:
            log.error(f"   HTTP error: {e.response.status_code} — {e.response.text[:300]}")
            post_results["status"] = "error"
            post_results["error"]  = str(e)

        except Exception as e:
            log.error(f"   Unexpected error: {e}")
            post_results["status"] = "error"
            post_results["error"]  = str(e)

        results.append(post_results)
        time.sleep(2)

    # Write results to log file
    log_path = Path(__file__).parent / "post_log.jsonl"
    with open(log_path, "a") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    # Summary
    posted  = sum(1 for r in results if r.get("status") == "posted")
    errors  = sum(1 for r in results if r.get("status") == "error")
    log.info(f"\n═══ Done  |  posted={posted}  errors={errors} ═══")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dr Liew social media auto-poster")
    parser.add_argument("--date",     default=str(date.today()), help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--dry-run",  action="store_true",        help="Show what would be posted without posting")
    parser.add_argument("--platform", default="all",              help="Platform filter: linkedin, facebook, instagram, or all (default: all)")
    args = parser.parse_args()

    # Validate date format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", args.date):
        log.error("--date must be in YYYY-MM-DD format")
        sys.exit(1)

    run(args.date, args.dry_run, args.platform)
