from fastapi.testclient import TestClient
import hashlib
from main import app

client = TestClient(app)


def test_tokens_endpoint():
    text = "hello world"
    count = 3
    resp = client.post(f"/tokens?count={count}", json={"text": text})
    assert resp.status_code == 200
    body = resp.json()
    assert "checksum" in body and "tokens" in body
    expected_checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert body["checksum"] == expected_checksum
    assert isinstance(body["tokens"], list)
    assert len(body["tokens"]) == count


def test_token_endpoint():
    text = "sample"
    resp = client.get(f"/token?text={text}")
    assert resp.status_code == 200
    body = resp.json()
    assert "checksum" in body and "token" in body
    expected_checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert body["checksum"] == expected_checksum
    assert isinstance(body["token"], str)
    assert body["token"].startswith(expected_checksum[:8])


def test_empty_text_post_returns_400():
    resp = client.post("/tokens", json={"text": ""})
    assert resp.status_code == 400
