# rate_limiter.py
import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

# memorie e thjeshtë: {IP: [timestamp1, timestamp2, ...]}
requests_store = defaultdict(list)
WINDOW = 60  # sekonda
MAX_CALLS = 5

def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr
        now = time.time()
        # fshi të vjetrit
        requests_store[ip] = [t for t in requests_store[ip] if now - t < WINDOW]
        if len(requests_store[ip]) >= MAX_CALLS:
            return jsonify({'error': 'Shumë kërkesa. Pritni 1 minutë.'}), 429
        requests_store[ip].append(now)
        return f(*args, **kwargs)
    return decorated