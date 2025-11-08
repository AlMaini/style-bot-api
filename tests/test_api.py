import requests


def test_api():
    url = "http://localhost:8080/api/try-on"
    with open("person.jpg", "rb") as p, open("cloth.png", "rb") as c:
        files = [
            ("images_files", ("person.jpg", p, "image/jpg")),
            ("images_files", ("cloth.png", c, "image/png")),
        ]
        response = requests.post(url, files=files)

    # Use the response so the variable is not unused; save output if successful.
    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        out_name = "result.png"
        with open(out_name, "wb") as out_f:
            _ = out_f.write(response.content)
        print(f"Saved response to {out_name} (Content-Type: {content_type})")
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")


if __name__ == "__main__":
    test_api()
