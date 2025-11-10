import hashlib, re
from urllib.parse import urlparse, urlunparse, parse_qsl
TRACKING_PARAMS={'utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','fbclid'}

def _normalize_title(t:str)->str:
    if not t: return ''
    return re.sub(r"\s+"," ",t.strip().lower())

def _normalize_url(u:str)->str:
    if not u: return ''
    parts=urlparse(u.strip())
    pairs=[(k,v) for k,v in parse_qsl(parts.query, keep_blank_values=True) if k not in TRACKING_PARAMS]
    sanitized=parts._replace(query='&'.join(f"{k}={v}" for k,v in pairs), fragment='')
    sanitized=sanitized._replace(netloc=sanitized.netloc.lower())
    return urlunparse(sanitized)

def fingerprint(title:str,url:str)->str:
    norm=f"{_normalize_title(title)}|{_normalize_url(url)}".encode('utf-8')
    return hashlib.sha256(norm).hexdigest()
