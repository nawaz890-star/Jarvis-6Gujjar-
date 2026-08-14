from core.app import CoreApp

def test_app_start_stop():
    app = CoreApp()
    app.start()
    assert app._running is True
    app.stop()
    assert app._running is False
