# scanner.py
import requests
import re
from config import GAMMA_API_URL

def extract_price_threshold(question):
    """מוציא מספרים מכותרת השאלה (למשל: 100k)"""
    match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*k?', question.lower())
    if match:
        val = match.group(1).replace(',', '')
        if 'k' in question.lower() and float(val) < 1000:
            return float(val) * 1000
        return float(val)
    return None

def scan_polymarket_for_hierarchical_markets():
    url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
    except Exception as e:
        print(f"Error fetching from Gamma API: {e}")
        return {}

    hierarchical_markets = {}
    for event in events:
        markets = event.get("markets", [])
        if len(markets) < 2: continue

        threshold_markets = []
        for market in markets:
            threshold = extract_price_threshold(market.get('question', ''))
            if threshold:
                threshold_markets.append({
                    "threshold": threshold,
                    "clob_token_id": market.get("clobTokenId"),
                    "condition_id": market.get("conditionId")
                })

        if len(threshold_markets) > 1:
            # מיון לפי מחיר היעד
            threshold_markets.sort(key=lambda x: x['threshold'])
            hierarchical_markets[event['title']] = {
                "clob_token_ids": [m["clob_token_id"] for m in threshold_markets if m["clob_token_id"]],
                "thresholds": [m["threshold"] for m in threshold_markets]
            }
    return hierarchical_markets