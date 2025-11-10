from urllib.parse import urlparse
WHITELIST={'kathmandupost.com':0.9,'ekantipur.com':0.85,'thehimalayantimes.com':0.85}

def reliability_score(url:str, has_author:bool, text_len:int)->float:
    try:
        host=urlparse(url).netloc.lower()
    except Exception:
        host=''
    base=WHITELIST.get(host,0.5)
    length_boost=min(text_len/2000.0,0.3)
    author_boost=0.1 if has_author else 0.0
    score=max(0.0,min(1.0, base+length_boost+author_boost))
    return round(score,4)
