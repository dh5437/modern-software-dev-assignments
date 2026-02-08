def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["id"] == item["id"]

    r = client.delete(f"/action-items/{item['id']}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 404


def test_action_item_validation_and_sort_errors(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422

    r = client.post("/action-items/", json={"description": "Valid"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.patch(f"/action-items/{item_id}", json={})
    assert r.status_code == 400

    r = client.get("/action-items/", params={"sort": "nope"})
    assert r.status_code == 400

def test_action_items_pagination_and_sorting(client):
    descriptions = ["Alpha task", "Bravo task", "Charlie task", "Delta task"]
    for desc in descriptions:
        r = client.post("/action-items/", json={"description": desc})
        assert r.status_code == 201, r.text

    r = client.get("/action-items/", params={"sort": "description", "limit": 2, "skip": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert [item["description"] for item in page1] == ["Alpha task", "Bravo task"]

    r = client.get("/action-items/", params={"sort": "description", "limit": 2, "skip": 2})
    assert r.status_code == 200
    page2 = r.json()
    assert [item["description"] for item in page2] == ["Charlie task", "Delta task"]

    r = client.get("/action-items/", params={"sort": "-description", "limit": 1, "skip": 0})
    assert r.status_code == 200
    page_desc = r.json()
    assert page_desc[0]["description"] == "Delta task"

