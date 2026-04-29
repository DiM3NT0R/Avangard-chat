import io

from fastapi.openapi.models import Response
from fastapi.testclient import TestClient

from tests.helpers.auth import auth_headers


def get_current_user(
    client: TestClient,
    access_token: str,
) -> dict:
    response = client.get(
        "/user/me",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200
    return response.json()


def upload_avatar(
    client: TestClient,
    access_token: str,
) -> Response:
    file_content = b"just some content"
    return client.post(
        "/user/me/avatar",
        headers=auth_headers(access_token),
        files={
            "file": ("avatar.jpg", io.BytesIO(file_content), "image/jpeg"),
        },
    )


def download_avatar(
    client: TestClient,
    access_token: str,
) -> Response:
    return client.get(
        "/user/me/avatar",
        headers=auth_headers(access_token),
    )
