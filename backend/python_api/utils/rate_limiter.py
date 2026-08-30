import time
from collections import defaultdict


class RateLimiter:
    """In-memory IP rate limiter to protect API endpoints from spam."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old timestamps
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]

        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False

    def get_retry_after(self, client_id: str) -> int:
        if not self.requests[client_id]:
            return 0
        oldest_request = self.requests[client_id][0]
        return max(1, int(self.window_seconds - (time.time() - oldest_request)))