# scanner.py
import requests
import re
import logging
from typing import Dict, List, Optional, Any
from config import GAMMA_API_URL, MAX_RETRIES, RETRY_DELAY
import time

logger = logging.getLogger(__name__)

def extract_price_threshold(question: str) -> Optional[float]:
    """Extract numerical threshold from market question string.
    
    Args:
        question: Market question text (e.g., "BTC above $100k?")
    
    Returns:
        Threshold value as float, or None if extraction fails
    """
    try:
        clean_q = question.replace('$', '').replace(',', '').lower()
        # Pattern matches: "100" "100k" "100.5" "100.5k"
        match = re.search(r'(\d+(?:\.\d+)?)\s*k?(?:\s|$|\?)', clean_q)
        if not match:
            return None
            
        val = float(match.group(1))
        # Handle 'k' suffix (e.g., 100k = 100000)
        if 'k' in clean_q[match.start():match.end()+1] and val < 1000:
            val *= 1000
        return val
    except (ValueError, AttributeError) as e:
        logger.debug(f"Failed to extract threshold from '{question}': {e}")
        return None

def extract_clob_token_id(market: Dict[str, Any]) -> Optional[str]:
    """Extract clobTokenId from market data, handling various formats.
    
    Args:
        market: Market dictionary from API response
    
    Returns:
        Clean token ID string, or None if not found
    """
    # Try clobTokenId field
    token_id = market.get("clobTokenId")
    if token_id:
        if isinstance(token_id, list) and len(token_id) > 0:
            token_id = token_id[0]
        if token_id:
            return str(token_id).strip()
    
    # Try clobTokenIds field
    token_ids = market.get("clobTokenIds")
    if isinstance(token_ids, list) and len(token_ids) > 0:
        return str(token_ids[0]).strip()
    
    return None

def scan_polymarket_for_hierarchical_markets(retry_count: int = 0) -> Dict[str, Any]:
    """Scan Gamma API for hierarchical/threshold-based markets.
    
    Hierarchical markets: Event with multiple threshold conditions
    (e.g., "BTC > 100k", "BTC > 105k", "BTC > 110k")
    
    Args:
        retry_count: Internal retry counter
    
    Returns:
        Dictionary mapping event titles to market data
    """
    url = f"{GAMMA_API_URL}/events?active=true&closed=false&limit=500"
    
    try:
        logger.info(f"Scanning Gamma API: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        events = response.json()
        
        if not isinstance(events, list):
            logger.error(f"Expected list from API, got: {type(events)}")
            return {}
            
    except requests.exceptions.Timeout:
        logger.error("Gamma API request timeout")
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return scan_polymarket_for_hierarchical_markets(retry_count + 1)
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from Gamma API: {e}")
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return scan_polymarket_for_hierarchical_markets(retry_count + 1)
        return {}
    except Exception as e:
        logger.error(f"Unexpected error scanning markets: {e}")
        return {}

    hierarchical_markets = {}
    
    for event in events:
        try:
            event_title = event.get('title', '')
            markets = event.get("markets", [])
            
            if len(markets) < 2:
                continue

            threshold_markets = []
            for market in markets:
                question = market.get('question', '')
                
                # Look for threshold indicators
                if not any(indicator in question.lower() for indicator in ['above', '>', 'over']):
                    continue
                
                threshold = extract_price_threshold(question)
                token_id = extract_clob_token_id(market)

                if threshold is not None and token_id:
                    threshold_markets.append({
                        "threshold": threshold,
                        "clob_token_id": token_id,
                        "title": question
                    })

            # Only include events with 2+ threshold markets
            if len(threshold_markets) >= 2:
                threshold_markets.sort(key=lambda x: x['threshold'])
                hierarchical_markets[event_title] = {
                    "clob_token_ids": [m["clob_token_id"] for m in threshold_markets],
                    "thresholds": [m["threshold"] for m in threshold_markets],
                    "market_count": len(threshold_markets)
                }
                logger.info(f"Found hierarchical market: {event_title} ({len(threshold_markets)} thresholds)")
                
        except Exception as e:
            logger.warning(f"Error processing event {event.get('title', 'unknown')}: {e}")
            continue
            
    logger.info(f"Total hierarchical markets found: {len(hierarchical_markets)}")
    return hierarchical_markets