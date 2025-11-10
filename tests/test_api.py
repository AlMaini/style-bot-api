import threading
from modulefinder import test

import requests


def test_api():
    url = "http://localhost:8080/api/try-on/single-item"
    with open("person.jpg", "rb") as p, open("clothing.jpg", "rb") as c:
        files = [
            ("images_files", ("person.jpg", p, "image/jpg")),
            ("images_files", ("clothing.jpg", c, "image/jpg")),
        ]
        response = requests.post(url, files=files)

    # Use the response so the variable is not unused; save output if successful.
    if response.status_code == 200:
        print("Request successful:", response.json()["job_id"])
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")


def test_jobs():
    """
    Send two concurrent requests to the /api/try-on/single-item endpoint using threads.
    Each thread opens its own file handles so they don't clash.
    The test asserts both responses are successful and include a job_id.
    """
    url = "http://localhost:8080/api/try-on/single-outfit"

    results = [None, None]

    def send_request(index: int):
        try:
            with open("person.jpg", "rb") as p, open("clothing.jpg", "rb") as c:
                files = [
                    ("images_files", ("person.jpg", p, "image/jpg")),
                    ("images_files", ("clothing.jpg", c, "image/jpg")),
                ]
                resp = requests.post(url, files=files)
                results[index] = resp
        except Exception as e:
            # Store the exception so the main thread can re-raise it
            results[index] = e

    threads = []
    for i in range(2):
        t = threading.Thread(target=send_request, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Validate results
    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            raise res
        assert res is not None, f"No response received for request #{idx}"
        assert res.status_code == 200, (
            f"Request #{idx} failed: {res.status_code} {res.text}"
        )
        json_body = res.json()
        assert "job_id" in json_body, (
            f"Request #{idx} response missing job_id: {json_body}"
        )

    print(
        "Both concurrent requests succeeded. Job IDs:",
        [r.json()["job_id"] for r in results],
    )


if __name__ == "__main__":
    # test_api()
    test_jobs()
