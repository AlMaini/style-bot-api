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


if __name__ == "__main__":
    test_api()
