import requests
from pathlib import Path


BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/v1"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PATH = PROJECT_ROOT / "backend" / "static" / "images" / "users" / "12001.jpg"


def main():
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": "faculty@example.com",
            "password": "password123",
            "role": "faculty",
        },
        timeout=20,
    )

    print("[INFO] login status:", login_response.status_code)
    print("[INFO] login body:", login_response.text)

    login_response.raise_for_status()
    token = login_response.json()["data"]["accessToken"]

    with open(IMAGE_PATH, "rb") as image_file:
        response = requests.post(
            f"{API_URL}/recognition/verify",
            headers={
                "Authorization": f"Bearer {token}",
            },
            files={
                "file": ("12001.jpg", image_file, "image/jpeg"),
            },
            data={
                "course": "Computer Science",
                "lecture_no": "99",
            },
            timeout=60,
        )

    print("[INFO] verify status:", response.status_code)
    print("[INFO] verify body:", response.text)


if __name__ == "__main__":
    main()