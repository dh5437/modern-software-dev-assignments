def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_action_item_validation(client):
    r = client.post("/action-items/", json={"description": " "})
    assert r.status_code == 400


def test_complete_action_item_not_found(client):
    r = client.put("/action-items/9999/complete")
    assert r.status_code == 404
