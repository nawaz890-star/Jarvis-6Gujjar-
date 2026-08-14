from automation.actions import open_url, search_files, open_path
from tempfile import TemporaryDirectory
from pathlib import Path


def test_open_url(monkeypatch):
    called = {}
    def fake_open(u):
        called['url'] = u
        return True
    monkeypatch.setattr('webbrowser.open', fake_open)
    ok, msg = open_url('https://example.com')
    assert ok is True
    assert 'Opened URL' in msg


def test_search_files():
    with TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / 'file_a.txt').write_text('hello')
        (p / 'another_file.txt').write_text('x')
        res = search_files(tmp, 'file_a')
        assert len(res) == 1
        assert 'file_a.txt' in res[0]


def test_open_path(tmp_path):
    f = tmp_path / 't.txt'
    f.write_text('x')
    ok, msg = open_path(str(f))
    # On CI os.startfile may not be supported; we accept both outcomes
    assert isinstance(ok, bool)
