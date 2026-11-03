# -*- coding: utf-8 -*-
"""登记表与文档不能各说各话。"""
from __future__ import annotations

from pathlib import Path

from cookline import rules

ROOT = Path(__file__).resolve().parents[1]


def test_registry_has_30_unique_ids():
    ids = [f["id"] for f in rules.FAILURES]
    assert len(ids) == 30
    assert len(set(ids)) == 30
    assert ids == [f"F{i:02d}" for i in range(1, 31)]


def test_every_failure_is_in_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for f in rules.FAILURES:
        assert f["id"] in readme, f"{f['id']} 没写进 README"
