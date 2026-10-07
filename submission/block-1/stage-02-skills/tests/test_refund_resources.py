"""Verify discoverable skill metadata and renamed documents using real file tools.

These checks do not assert model behavior or fabricate an agent conversation.
"""

import json
from pathlib import Path
import shutil

import paths
from skill_catalog import scan_skills
from tools import list_files, read_file


def test_refund_catalog_and_reference_are_readable(monkeypatch):
    workspace = paths.PROJECT_ROOT / "workspace"
    monkeypatch.setattr(paths, "WORKSPACE_DIR", workspace)
    catalog = scan_skills(workspace)
    entry = next(s for s in catalog.skills if s.name == "refund-policy")
    assert entry.location == "skills/refund-policy/SKILL.md"
    assert entry.description and not catalog.diagnostics
    for path in [entry.location, "skills/refund-policy/references/answer-template.md"]:
        result = json.loads(read_file.invoke({"path": path}))
        assert result["ok"] is True and result["content"]


def test_renaming_preserves_discovery_and_content(tmp_path, monkeypatch):
    source = paths.PROJECT_ROOT / "workspace/data/policies"
    workspace = tmp_path / "workspace"
    target = workspace / "data/policies"
    shutil.copytree(source, target)
    contents = {p.read_text(encoding="utf-8") for p in target.glob("*.md")}
    for index, path in enumerate(sorted(target.glob("*.md"))):
        path.rename(path.with_name(f"renamed-{index}.md"))
    monkeypatch.setattr(paths, "WORKSPACE_DIR", workspace)
    result = json.loads(list_files.invoke({"path": "data/policies"}))
    assert result["ok"] is True and len(result["entries"]) == 2
    discovered = set()
    for entry in result["entries"]:
        assert entry["name"].startswith("renamed-")
        read = json.loads(read_file.invoke({"path": entry["path"]}))
        assert read["ok"] is True
        discovered.add(read["content"])
    assert discovered == contents
