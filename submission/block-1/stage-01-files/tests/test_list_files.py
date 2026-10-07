"""Directory discovery with real workspace paths and structured errors."""

import json

import pytest

import paths
from tools import files


@pytest.fixture
def ws(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "data").mkdir(parents=True)
    (workspace / "output").mkdir()
    (workspace / "data" / "note.md").write_text("Xin chào", encoding="utf-8")
    return workspace


def listing(workspace, path):
    assert hasattr(files, "_list"), "list_files implementation is missing"
    return files._list(workspace, path)


def test_direct_entries_are_sorted_and_workspace_relative(ws):
    (ws / "data" / "a-folder").mkdir()
    (ws / "data" / "a-folder" / "nested.md").write_text("nested")
    (ws / "data" / "z.md").write_text("last")
    assert listing(ws, "data") == {
        "ok": True,
        "path": "data",
        "entries": [
            {"name": "a-folder", "path": "data/a-folder", "type": "directory"},
            {"name": "note.md", "path": "data/note.md", "type": "file"},
            {"name": "z.md", "path": "data/z.md", "type": "file"},
        ],
    }


def test_empty_directory_is_valid(ws):
    assert listing(ws, "output") == {"ok": True, "path": "output", "entries": []}


@pytest.mark.parametrize("path,code", [
    ("data/note.md", "NOT_A_DIRECTORY"),
    ("missing", "DIRECTORY_NOT_FOUND"),
    ("../outside", "PATH_OUTSIDE_WORKSPACE"),
    ("data/../../outside", "PATH_OUTSIDE_WORKSPACE"),
    ("", "INVALID_PATH"),
])
def test_invalid_directories_return_errors(ws, path, code):
    result = listing(ws, path)
    assert result["ok"] is False
    assert result["error"]["code"] == code
    assert "entries" not in result


def test_absolute_directory_is_rejected(ws):
    assert listing(ws, str(ws / "data"))["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def make_link(link, target, directory):
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows account cannot create symlinks")
        raise


def test_symlink_directory_escape_is_rejected(ws):
    outside = ws.parent / "outside"
    outside.mkdir()
    (outside / "dummy.md").write_text("synthetic data")
    make_link(ws / "escape", outside, True)
    assert listing(ws, "escape")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_listing_rejects_child_symlink_outside_workspace(ws):
    outside = ws.parent / "dummy.md"
    outside.write_text("synthetic data")
    make_link(ws / "data" / "escape.md", outside, False)
    assert listing(ws, "data")["error"]["code"] == "PATH_OUTSIDE_WORKSPACE"


def test_json_tool_and_schema(ws, monkeypatch):
    assert hasattr(files, "list_files"), "registered tool is missing"
    monkeypatch.setattr(paths, "WORKSPACE_DIR", ws)
    result = json.loads(files.list_files.invoke({"path": "data"}))
    assert result["ok"] is True
    assert result["entries"][0]["path"] == "data/note.md"
    schema = files.list_files.args_schema.model_json_schema()
    assert schema["required"] == ["path"]
    assert schema["properties"]["path"]["type"] == "string"
