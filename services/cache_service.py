# cache_service.py
import os
import json
import hashlib
import time
from config import config

CACHE_DIR = os.path.join(config.UPLOAD_FOLDER, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_key(url, search_text):
    "Unique key per URL + fjale"
    return hashlib.md5(f"{url.strip()}|{search_text.strip()}".encode()).hexdigest()

def get_cached_result(url, search_text, max_age_seconds=24*60*60):
    key = _cache_key(url, search_text)
    meta_file = os.path.join(CACHE_DIR, f"{key}.json")
    shot_file = os.path.join(CACHE_DIR, f"{key}.png")

    if not (os.path.exists(meta_file) and os.path.exists(shot_file)):
        return None

    if time.time() - os.path.getmtime(meta_file) > max_age_seconds:
        # expired
        os.remove(meta_file); os.remove(shot_file)
        return None

    with open(meta_file, 'r', encoding='utf-8') as f:
        return json.load(f)  # {matches, score, screenshot_url}

def save_cache(url, search_text, matches, score, screenshot_path):
    key = _cache_key(url, search_text)
    meta_file = os.path.join(CACHE_DIR, f"{key}.json")
    shot_file = os.path.join(CACHE_DIR, f"{key}.png")

    # Kopjo screenshot në cache
    if os.path.exists(screenshot_path):
        os.replace(screenshot_path, shot_file)

    meta = {
        'matches': matches,
        'score': score,
        'screenshot_url': f"/static/uploads/cache/{key}.png"
    }
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

# --- plug-and-play në scraper_service.py ----
# from services.cache_service import get_cached_result, save_cache
#
# Në fillim të scrape_and_screenshots:
#   cached = get_cached_result(url, search_text)
#   if cached:  return {'success':True, 'results':[cached]}
#
# Pas ocr_search:
#   save_cache(page_url, search_text, ocr_search['matches'], score, save_path)