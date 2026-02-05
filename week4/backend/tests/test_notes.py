def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    note_id = data["id"]

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/", params={"q": "hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "Changed"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "Updated"

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_note_validation(client):
    r = client.post("/notes/", json={"title": " ", "content": "Valid"})
    assert r.status_code == 400

    r = client.post("/notes/", json={"title": "Valid", "content": " "})
    assert r.status_code == 400

    r = client.put("/notes/9999", json={})
    assert r.status_code == 400


def test_extract_from_note_creates_action_items(client):
    payload = {"title": "Extract", "content": "TODO: follow up\nShip it! #tag"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    items = r.json()
    assert any(item["description"] == "TODO: follow up" for item in items)
    assert any(item["description"] == "Ship it!" for item in items)
    assert any(item["description"] == "#tag" for item in items)


def test_search_with_whitespace_query_returns_all(client):
    client.post("/notes/", json={"title": "A", "content": "Alpha"})
    client.post("/notes/", json={"title": "B", "content": "Beta"})

    r = client.get("/notes/search/", params={"q": "   "})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2


def test_update_note_partial_fields(client):
    r = client.post("/notes/", json={"title": "T", "content": "C"})
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "T2"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "T2"
    assert updated["content"] == "C"


def test_delete_note_not_found(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404
