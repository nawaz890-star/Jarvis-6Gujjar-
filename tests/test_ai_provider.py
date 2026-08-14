from ai.fallback import fallback_response

def test_fallback_response():
    r = fallback_response("hello jarvis")
    assert "I am offline" in r
