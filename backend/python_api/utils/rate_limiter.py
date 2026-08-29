import time
import logging

from collections import defaultdict
from threading import Lock


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Limits requests based on client IP address.
    """

    def __init__(
        self,
        max_requests: int = 30,
        window_seconds: int = 60,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self.requests = defaultdict(list)

        self.lock = Lock()

    def is_allowed(
        self,
        client_id: str,
    ) -> bool:
        """
        Check whether a client is allowed
        to make another request.
        """

        current_time = time.time()

        with self.lock:

            request_times = self.requests[
                client_id
            ]

            # -----------------------------------------
            # Remove expired requests
            # -----------------------------------------

            request_times[:] = [
                request_time
                for request_time in request_times
                if current_time - request_time
                < self.window_seconds
            ]

            # -----------------------------------------
            # Check request limit
            # -----------------------------------------

            if len(request_times) >= self.max_requests:

                logger.warning(
                    "Rate limit exceeded: %s",
                    client_id
                )

                return False

            # -----------------------------------------
            # Record current request
            # -----------------------------------------

            request_times.append(
                current_time
            )

            return True

    def get_retry_after(
        self,
        client_id: str,
    ) -> int:
        """
        Return approximately how many seconds
        the client should wait before retrying.
        """

        current_time = time.time()

        with self.lock:

            request_times = self.requests.get(
                client_id,
                []
            )

            if not request_times:
                return 0

            oldest_request = min(
                request_times
            )

            remaining = (
                self.window_seconds
                - (current_time - oldest_request)
            )

            return max(
                1,
                int(remaining)
            )

        rate_limiter = RateLimiter(
            max_requests=30,
            window_seconds=60,
)