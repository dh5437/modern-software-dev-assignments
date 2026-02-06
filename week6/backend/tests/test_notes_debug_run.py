from types import SimpleNamespace


def test_debug_run_allows_echo_and_uses_shell_false(client, monkeypatch):
    captured = {}

    def fake_run(args, shell, capture_output, text):
        captured["args"] = args
        captured["shell"] = shell
        captured["capture_output"] = capture_output
        captured["text"] = text
        return SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    import subprocess

    monkeypatch.setattr(subprocess, "run", fake_run)

    r = client.get("/notes/debug/run", params={"cmd": "echo ok"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["returncode"] == "0"
    assert body["stdout"] == "ok\n"
    assert body["stderr"] == ""
    assert captured["args"] == ["echo", "ok"]
    assert captured["shell"] is False
    assert captured["capture_output"] is True
    assert captured["text"] is True


def test_debug_run_rejects_empty_command(client):
    r = client.get("/notes/debug/run", params={"cmd": ""})
    assert r.status_code == 400
    assert r.json()["detail"] == "Command required"


def test_debug_run_rejects_non_allowlisted_command(client):
    r = client.get("/notes/debug/run", params={"cmd": "ls"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Command not allowed"
