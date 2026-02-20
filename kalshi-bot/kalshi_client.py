#!/usr/bin/env python3
"""Kalshi API v2 client with RSA-PSS authentication."""
import os, time, base64, json, requests
from typing import Optional
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BASE_URL = os.getenv('KALSHI_BASE_URL', 'https://api.elections.kalshi.com/trade-api/v2')
API_KEY_ID = os.getenv('KALSHI_API_KEY_ID')
PRIVATE_KEY_PEM = os.getenv('KALSHI_PRIVATE_KEY')


class KalshiClient:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key_id = API_KEY_ID
        self.private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PEM.encode(), password=None
        )
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _sign(self, message: str) -> str:
        sig = self.private_key.sign(
            message.encode('utf-8'),
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')

    def _auth_headers(self, method: str, path: str) -> dict:
        ts = str(int(time.time() * 1000))
        msg = ts + method.upper() + path
        return {
            'KALSHI-ACCESS-KEY': self.api_key_id,
            'KALSHI-ACCESS-TIMESTAMP': ts,
            'KALSHI-ACCESS-SIGNATURE': self._sign(msg),
        }

    def _get(self, path: str, params: dict = None, auth: bool = True) -> dict:
        url = self.base_url + path
        headers = self._auth_headers('GET', '/trade-api/v2' + path) if auth else {}
        resp = self.session.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict) -> dict:
        url = self.base_url + path
        headers = self._auth_headers('POST', '/trade-api/v2' + path)
        resp = self.session.post(url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> dict:
        url = self.base_url + path
        headers = self._auth_headers('DELETE', '/trade-api/v2' + path)
        resp = self.session.delete(url, headers=headers)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    # ── Account ──────────────────────────────────────────────────────────────

    def get_balance(self) -> dict:
        """Returns balance in cents. Divide by 100 for dollars."""
        return self._get('/portfolio/balance')

    def get_positions(self) -> list:
        data = self._get('/portfolio/positions')
        return data.get('market_positions', [])

    def get_orders(self, status: str = None) -> list:
        params = {}
        if status:
            params['status'] = status
        data = self._get('/portfolio/orders', params=params)
        return data.get('orders', [])

    def get_fills(self) -> list:
        data = self._get('/portfolio/fills')
        return data.get('fills', [])

    def get_settlements(self) -> list:
        data = self._get('/portfolio/settlements')
        return data.get('settlements', [])

    # ── Markets ───────────────────────────────────────────────────────────────

    def get_markets(self, limit: int = 200, cursor: str = None,
                    status: str = 'open', min_close_ts: int = None,
                    max_close_ts: int = None) -> dict:
        params = {'limit': limit, 'status': status}
        if cursor:
            params['cursor'] = cursor
        if min_close_ts:
            params['min_close_ts'] = min_close_ts
        if max_close_ts:
            params['max_close_ts'] = max_close_ts
        return self._get('/markets', params=params, auth=False)

    def get_all_markets(self, status: str = 'open', max_pages: int = 10) -> list:
        """
        Fetch real tradeable markets by scanning known series.
        The generic /markets endpoint only returns MVE parlay markets.
        """
        # Curated list of series with real economic/political/weather markets
        TARGET_SERIES = [
            'KXFED',       # Federal Reserve rate decisions
            'KXCPI',       # CPI / inflation prints
            'KXGDP',       # GDP growth
            'KXFRM',       # Mortgage rates
            'KXECONSTAT',  # Economic statistics
            'KXBTCPRICE',  # Bitcoin price
            'KXINX',       # S&P 500
            'KXSPY',       # S&P 500 ETF
            'KXDOGE',      # DOGE / gov spending
            'KXTRUMP',     # Trump policy markets
            'KXTARIFF',    # Tariffs
            'KXGOV',       # Government shutdown / debt ceiling
            'KXFEDEND',    # Fed ending
            'KXFEDCHAIRNOM', # Fed Chair
            'KXAVGTARIFF', # Average tariff rate
        ]

        # Also target current FOMC event directly
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        year2 = str(now.year)[2:]
        next_months = []
        for m in range(now.month, now.month + 4):
            mon = m % 12 or 12
            yr = year2 if m <= 12 else str(int(year2) + 1)
            next_months.append(f"{yr}{mon:02d}")

        event_tickers = [f"KXFED-{m}" for m in [
            f"26MAR", f"26MAY", f"26JUN", f"26JUL", f"26SEP",
            f"26NOV", f"26DEC", f"27JAN", f"27MAR", f"27APR"
        ]] + [
            f"KXCPI-26FEB", f"KXCPI-26MAR", f"KXCPI-26APR",
        ]

        markets = []
        seen = set()

        # Scan by series_ticker
        for series in TARGET_SERIES:
            try:
                data = self.get_markets(limit=200, status=status)
                # Use series_ticker param directly
                r = self.session.get(
                    f'{self.base_url}/markets',
                    params={'limit': 200, 'series_ticker': series}
                )
                if r.ok:
                    batch = r.json().get('markets', [])
                    for m in batch:
                        t = m.get('ticker', '')
                        if t not in seen:
                            seen.add(t)
                            markets.append(m)
                time.sleep(0.3)
            except Exception:
                pass

        # Scan by event_ticker for key upcoming events
        for event_ticker in event_tickers:
            try:
                r = self.session.get(
                    f'{self.base_url}/markets',
                    params={'limit': 50, 'event_ticker': event_ticker}
                )
                if r.ok:
                    batch = r.json().get('markets', [])
                    for m in batch:
                        t = m.get('ticker', '')
                        if t not in seen:
                            seen.add(t)
                            markets.append(m)
                time.sleep(0.2)
            except Exception:
                pass

        return markets

    def get_market(self, ticker: str) -> dict:
        data = self._get(f'/markets/{ticker}', auth=False)
        return data.get('market', data)

    def get_orderbook(self, ticker: str) -> dict:
        data = self._get(f'/markets/{ticker}/orderbook', auth=False)
        return data.get('orderbook', data)

    def get_events(self, limit: int = 200) -> list:
        data = self._get('/events', params={'limit': limit}, auth=False)
        return data.get('events', [])

    # ── Trading ───────────────────────────────────────────────────────────────

    def place_order(self, ticker: str, action: str, side: str,
                    order_type: str, count: int, price: int) -> dict:
        """
        ticker: market ticker
        action: 'buy' or 'sell'
        side: 'yes' or 'no'
        order_type: 'limit' or 'market'
        count: number of contracts
        price: price in cents (1-99)
        """
        body = {
            'ticker': ticker,
            'action': action,
            'side': side,
            'type': order_type,
            'count': count,
        }
        if side == 'yes':
            body['yes_price'] = price
        else:
            body['no_price'] = price
        return self._post('/portfolio/orders', body)

    def cancel_order(self, order_id: str) -> dict:
        return self._delete(f'/portfolio/orders/{order_id}')


if __name__ == '__main__':
    client = KalshiClient()
    bal = client.get_balance()
    balance_cents = bal.get('balance', 0)
    print(f"Balance: ${balance_cents/100:.2f}")
    print(f"Portfolio value: ${bal.get('portfolio_value', 0)/100:.2f}")
