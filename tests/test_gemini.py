import os

from dotenv import load_dotenv

import robin_stocks.gemini as g

load_dotenv()


class TestAuthentication:
    def test_login(self):
        g.login(os.environ["GEMINI_ACCOUNT_KEY"], os.environ["GEMINI_ACCOUNT_SECRET"])
        assert g.get_login_state()

    def test_logout(self):
        g.login(os.environ["GEMINI_ACCOUNT_KEY"], os.environ["GEMINI_ACCOUNT_SECRET"])
        g.logout()
        assert not g.get_login_state()

    def test_heartbeat(self):
        g.login(os.environ["GEMINI_ACCOUNT_KEY"], os.environ["GEMINI_ACCOUNT_SECRET"])
        response, err = g.heartbeat()
        data = response.json()
        assert err is None
        assert response.status_code == 200
        assert data["result"] == "ok"


class TestCrypto:
    ticker = "btcusd"

    def test_pubticker_btc(self):
        response, err = g.get_pubticker(self.ticker)
        data = response.json()
        assert err is None
        assert response.status_code == 200
        assert "bid" in data
        assert "ask" in data
        assert "volume" in data
        assert "last" in data

    def test_get_symbols(self):
        response, err = g.get_symbols()
        data = response.json()
        assert err is None
        assert response.status_code == 200
        assert len(data) > 1
        assert self.ticker in data


class TestOrders:
    ticker = "ethusd"

    @classmethod
    def setup_class(cls):
        g.use_sand_box_urls(True)
        g.login(os.environ["GEMINI_SANDBOX_KEY"], os.environ["GEMINI_SANDBOX_SECRET"])

    @classmethod
    def teardown_class(cls):
        g.use_sand_box_urls(False)

    def test_mytrades(self):
        response, err = g.get_trades_for_crypto("btcusd")
        assert err is None
        assert response.status_code == 200


class TestAccount:
    @classmethod
    def setup_class(cls):
        g.login(os.environ["GEMINI_ACCOUNT_KEY"], os.environ["GEMINI_ACCOUNT_SECRET"])

    def test_account_detail(self):
        response, err = g.get_account_detail()
        assert err is None
        assert response.status_code == 200
