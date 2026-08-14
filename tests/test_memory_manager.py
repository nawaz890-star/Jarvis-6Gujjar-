from memory.manager import LongTermMemory
from tempfile import TemporaryDirectory
from pathlib import Path


def test_memory_add_get_delete():
    with TemporaryDirectory() as tmp:
        dbp = Path(tmp) / "mem.db"
        lm = LongTermMemory(db_path=dbp)
        # add
        id1 = lm.add("favorite_editor", "vscode")
        assert isinstance(id1, int) and id1 > 0
        # get
        rows = lm.get("favorite_editor")
        assert len(rows) >= 1
        assert rows[0]["value"] == "vscode"
        # list
        all_rows = lm.list_keys()
        assert any(r["key"] == "favorite_editor" for r in all_rows)
        # delete
        deleted = lm.delete(id1)
        assert deleted is True
        # clear
        lm.add("a","b")
        lm.clear_all()
        assert lm.list_keys() == []
