import concurrent.futures
import time
from typing import Dict, List, Optional, Tuple

import requests


def login(email: str, password: str) -> str:
    """
    Return an access token for the given credentials.
    """
    url = "http://localhost:8080/api/auth/login"
    payload = {"email": email, "password": password}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["access_token"]


def test_job() -> Tuple[str, str]:
    """
    Start a single job and return a tuple (job_id, token).

    NOTE: The request opens files; they are closed before returning.
    """
    token = login("abdullahalmaini2017@gmail.com", "Abdullah10")

    url = "http://localhost:8080/api/try-on/single-outfit"
    headers = {"Authorization": f"Bearer {token}"}

    # Use context managers so file descriptors are closed right away.
    with (
        open("tests/person.jpg", "rb") as person_f,
        open("tests/clothing.png", "rb") as clothing_f,
    ):
        files = [
            ("person_file", ("person.jpg", person_f, "image/jpeg")),
            ("clothing_files", ("clothing.png", clothing_f, "image/png")),
        ]

        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        job_id = response.json().get("job_id")
        if not job_id:
            raise RuntimeError("No job_id returned from start-job endpoint")
        return job_id, token


def get_job_status(job_id: str, token: Optional[str] = None) -> Dict:
    """
    Attempt to fetch the status for `job_id`.

    This function tries a small set of reasonable endpoint patterns and returns
    the parsed JSON from the first successful endpoint that contains a
    'status' key. If none succeed, returns the last response JSON or an empty dict.

    If your API exposes a different status endpoint, update `endpoints_to_try`.
    """
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    endpoint = f"http://localhost:8080/api/status/progress/{job_id}"
    last_json = {}
    try:
        resp = requests.get(endpoint, headers=headers, timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch job status for job_id={job_id}")
        parsed = resp.json()
        last_json = parsed
        # Expecting the API to expose a `status` field for progress.
        if isinstance(parsed, dict) and "status" in parsed:
            return parsed
    except requests.RequestException:
        raise RuntimeError(f"Failed to fetch job status for job_id={job_id}")

    return last_json


def poll_job_until_done(
    job_id: str, token: Optional[str], poll_interval: float = 1.0
) -> Dict:
    """
    Poll a single job's status until it's finished. Returns the final status JSON.

    Prints live progress to stdout so the test can observe updates.
    """
    while True:
        status_json = get_job_status(job_id, token)
        status = None
        if isinstance(status_json, dict):
            # Accept both 'status' or fallback keys if the API returns different shape
            status = status_json.get("status")

        print(f"[job {job_id}] polled status: {status_json}")
        # If status is a string and in terminal_states we stop polling.
        if isinstance(status, str) and status.strip().lower() == "completed":
            return status_json

        # If response contained enough info to determine completion by other keys,
        # you can extend logic here.

        time.sleep(poll_interval)


def run_jobs_concurrently(
    n: int,
    poll_interval: float = 1.0,
    start_max_workers: int = 10,
    poll_max_workers: int = 10,
) -> Dict[str, Dict]:
    """
    Start `n` jobs concurrently, poll each job's status concurrently to provide live
    progress, and return a mapping job_id -> final status JSON when all complete.

    Usage:
        final_statuses = run_jobs_concurrently(5)

    Returns:
        Dict[job_id, final_status_json]
    """
    started_jobs: List[Tuple[str, str]] = []

    # Start jobs concurrently
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=start_max_workers
    ) as executor:
        start_futures = [executor.submit(test_job) for _ in range(n)]
        for fut in concurrent.futures.as_completed(start_futures):
            try:
                job_id, token = fut.result()
                print(f"Started job {job_id}")
                started_jobs.append((job_id, token))
            except Exception as e:
                print(f"Failed to start a job: {e}")

    # Poll all jobs concurrently
    final_results: Dict[str, Dict] = {}

    def _poll_and_store(job_id_token: Tuple[str, str]):
        job_id, token = job_id_token
        final = poll_job_until_done(job_id, token, poll_interval=poll_interval)
        final_results[job_id] = final

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=poll_max_workers
    ) as poll_executor:
        poll_futures = [
            poll_executor.submit(_poll_and_store, jt) for jt in started_jobs
        ]
        # Wait for all polls to complete
        for fut in concurrent.futures.as_completed(poll_futures):
            try:
                fut.result()
            except Exception as e:
                print(f"Polling task raised: {e}")

    print("All jobs have reached terminal state.")
    return final_results


if __name__ == "__main__":
    # Simple demo runner when executing the file directly.
    # In a real test, you'd call `run_jobs_concurrently(...)` from your test harness.
    results = run_jobs_concurrently(1, poll_interval=2.0)
    print("Final results:")
    for jid, res in results.items():
        print(jid, res)
