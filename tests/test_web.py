from web.search import search
from web.weather import geocode_city, get_weather_by_city


def test_search_monkeypatch(monkeypatch):
    sample_html = '''
    <html><body>
    <div class="result">
      <a class="result__a" href="https://example.com">Example Domain</a>
      <div class="result__snippet">An example website</div>
    </div>
    </body></html>
    '''
    class FakeResp:
        text = sample_html
        status_code = 200
        def raise_for_status(self):
            return None
    def fake_post(url, data=None, headers=None, timeout=None):
        return FakeResp()
    monkeypatch.setattr('requests.post', fake_post)
    results = search('example query', max_results=2, auto_open_top=False)
    assert len(results) >= 1
    assert results[0][1] == 'https://example.com'


def test_geocode_monkeypatch(monkeypatch):
    sample_json = {"results": [{"name": "Springfield", "latitude": 40.0, "longitude": -75.0}]}
    class FakeResp:
        def json(self):
            return sample_json
        def raise_for_status(self):
            return None
    def fake_get(url, params=None, timeout=None):
        return FakeResp()
    monkeypatch.setattr('requests.get', fake_get)
    g = geocode_city('Springfield')
    assert g['latitude'] == 40.0
