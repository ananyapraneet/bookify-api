import statistics
import time

import requests

BASE_URL = "http://127.0.0.1:8000"
ITERATIONS = 20


def measure_request(url: str, headers: dict) -> float:
    start = time.perf_counter()

    response = requests.get(
        url,
        headers=headers,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    return elapsed * 1000


def print_results(title: str, timings: list[float]) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    print(f"Requests: {len(timings)}")
    print(f"Min:      {min(timings):.2f} ms")
    print(f"Max:      {max(timings):.2f} ms")
    print(f"Average:  {statistics.mean(timings):.2f} ms")
    print(f"Median:   {statistics.median(timings):.2f} ms")


def main():
    token = input("Enter JWT access token: ").strip()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = f"{BASE_URL}/services"

    print("\nWarming up API...")

    response = requests.get(
        url,
        headers=headers,
    )

    response.raise_for_status()

    print("API is reachable.")

    # ---------------------------------------------------------
    # CACHE MISS / DATABASE PATH
    # ---------------------------------------------------------

    print("\nBenchmarking database path...")

    database_timings = []

    for _ in range(ITERATIONS):
        # Remove the services cache before every request.
        import redis

        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
        )

        redis_client.delete("services:list")

        elapsed = measure_request(
            url,
            headers,
        )

        database_timings.append(elapsed)

    print_results(
        "Database / Cache-Miss Path",
        database_timings,
    )

    # ---------------------------------------------------------
    # CACHE HIT PATH
    # ---------------------------------------------------------

    print("\nBenchmarking Redis cache-hit path...")

    cache_timings = []

    # First request populates Redis.
    measure_request(
        url,
        headers,
    )

    for _ in range(ITERATIONS):
        elapsed = measure_request(
            url,
            headers,
        )

        cache_timings.append(elapsed)

    print_results(
        "Redis / Cache-Hit Path",
        cache_timings,
    )

    # ---------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------

    database_average = statistics.mean(database_timings)
    cache_average = statistics.mean(cache_timings)

    improvement = (
        (database_average - cache_average)
        / database_average
    ) * 100

    speedup = database_average / cache_average

    print("\nPerformance Comparison")
    print("======================")

    print(
        f"Database average: {database_average:.2f} ms"
    )

    print(
        f"Redis average:    {cache_average:.2f} ms"
    )

    print(
        f"Latency reduction: {improvement:.2f}%"
    )

    print(
        f"Approx. speedup:  {speedup:.2f}x"
    )


if __name__ == "__main__":
    main()
