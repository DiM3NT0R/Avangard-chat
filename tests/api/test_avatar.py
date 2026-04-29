from fastapi.testclient import TestClient

from tests.helpers.auth import register_user
from tests.helpers.user_profile import download_avatar, get_current_user, upload_avatar


def test_upload_avatar_successful(client: TestClient):
    alice = register_user(client, "dm-alice")

    response = upload_avatar(
        client,
        alice["access_token"],
    )

    assert response.status_code == 200
    avatar = response.json()["avatar"]

    assert avatar is not None

    user = get_current_user(
        client,
        alice["access_token"],
    )

    assert avatar == user["avatar"]


def test_download_avatar_successful(client: TestClient):
    alice = register_user(client, "dm-alice")

    upload_avatar(
        client,
        alice["access_token"],
    )

    response = download_avatar(
        client,
        alice["access_token"],
    )

    assert response.status_code == 200


def test_download_avatar_not_found(client: TestClient):
    alice = register_user(client, "dm-alice")

    response = download_avatar(
        client,
        alice["access_token"],
    )

    assert response.status_code == 400
