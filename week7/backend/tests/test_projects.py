def test_create_project_and_link_items(client):
    project_payload = {"name": "Alpha", "description": "First project"}
    r = client.post("/projects/", json=project_payload)
    assert r.status_code == 201, r.text
    project = r.json()
    project_id = project["id"]

    r = client.get("/projects/")
    assert r.status_code == 200
    assert any(p["id"] == project_id for p in r.json())

    r = client.post("/notes/", json={"title": "Note", "content": "Body", "project_id": project_id})
    assert r.status_code == 201, r.text
    note = r.json()
    assert note["project_id"] == project_id

    r = client.post("/action-items/", json={"description": "Ship", "project_id": project_id})
    assert r.status_code == 201, r.text
    action_item = r.json()
    assert action_item["project_id"] == project_id

    r = client.get("/notes/", params={"project_id": project_id})
    assert r.status_code == 200
    assert any(n["id"] == note["id"] for n in r.json())

    r = client.get("/action-items/", params={"project_id": project_id})
    assert r.status_code == 200
    assert any(i["id"] == action_item["id"] for i in r.json())


def test_project_validation_errors(client):
    r = client.post("/notes/", json={"title": "Note", "content": "Body", "project_id": 999})
    assert r.status_code == 404

    r = client.post("/action-items/", json={"description": "Ship", "project_id": 999})
    assert r.status_code == 404
