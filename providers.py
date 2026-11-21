import os, requests

class ProviderError(RuntimeError):
    pass

class UpstoxClient:
    BASE = "https://api.upstox.com/v2"
    def __init__(self, token):
        self.token = token

    def _get(self, path, params=None):
        response = requests.get(
            self.BASE + path,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
            params=params, timeout=20
        )
        if response.status_code >= 400:
            raise ProviderError(f"Upstox API returned HTTP {response.status_code}: {response.text[:250]}")
        body = response.json()
        if body.get("status") == "error":
            raise ProviderError(str(body.get("errors") or body)[:250])
        return body.get("data", body)

    def profile(self):
        return self._get("/user/profile")

def demo_market_snapshot():
    # Clearly-labelled sample values; never represent these as live prices.
    return [
        {"symbol":"RELIANCE","name":"Reliance Industries","price":1450.0,"change_pct":1.2,"source":"DEMO"},
        {"symbol":"HDFCBANK","name":"HDFC Bank","price":980.0,"change_pct":-0.4,"source":"DEMO"},
        {"symbol":"BHARTIARTL","name":"Bharti Airtel","price":1625.0,"change_pct":0.8,"source":"DEMO"},
    ]
