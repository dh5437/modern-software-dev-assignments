def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_notes_pagination_and_sorting(client):
    titles = ["Alpha", "Bravo", "Charlie", "Delta"]
    for title in titles:
        r = client.post("/notes/", json={"title": title, "content": f"{title} body"})
        assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"sort": "title", "limit": 2, "skip": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert [item["title"] for item in page1] == ["Alpha", "Bravo"]

    r = client.get("/notes/", params={"sort": "title", "limit": 2, "skip": 2})
    assert r.status_code == 200
    page2 = r.json()
    assert [item["title"] for item in page2] == ["Charlie", "Delta"]

    r = client.get("/notes/", params={"sort": "-title", "limit": 1, "skip": 0})
    assert r.status_code == 200
    page_desc = r.json()
    assert page_desc[0]["title"] == "Delta"

