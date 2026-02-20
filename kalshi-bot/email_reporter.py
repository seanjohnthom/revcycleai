#!/usr/bin/env python3
"""
Daily Kalshi P&L email report.
Sends a clean win/loss summary to seanjohnthompson@gmail.com via Resend API.
"""
import os, json, requests
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
FROM_EMAIL     = 'ClawdBot <onboarding@resend.dev>'  # Updated once domain verified
TO_EMAIL       = 'seanjohnthompson@gmail.com'
WORKSPACE      = Path(__file__).parent


def load_ledger() -> list:
    ledger_path = WORKSPACE / 'trade_ledger.json'
    if ledger_path.exists():
        return json.loads(ledger_path.read_text())
    return []


def build_report(trades: list) -> dict:
    """Summarize ledger into P&L stats."""
    settled   = [t for t in trades if t.get('pnl') is not None]
    open_pos  = [t for t in trades if t.get('status') in ('open', 'resting')]
    wins      = [t for t in settled if t.get('pnl', 0) > 0]
    losses    = [t for t in settled if t.get('pnl', 0) < 0]

    total_pnl      = sum(t.get('pnl', 0) for t in settled)
    total_wagered  = sum(t.get('cost', 0) for t in settled)
    open_exposure  = sum(t.get('cost', 0) for t in open_pos)
    win_rate       = len(wins) / len(settled) * 100 if settled else 0

    return {
        'date': date.today().isoformat(),
        'total_trades': len(trades),
        'settled': len(settled),
        'open': len(open_pos),
        'wins': len(wins),
        'losses': len(losses),
        'total_pnl': round(total_pnl, 2),
        'total_wagered': round(total_wagered, 2),
        'open_exposure': round(open_exposure, 2),
        'win_rate': round(win_rate, 1),
        'win_details': wins,
        'loss_details': losses,
        'open_details': open_pos,
    }


def format_email_html(r: dict) -> str:
    pnl_color   = '#27ae60' if r['total_pnl'] >= 0 else '#e74c3c'
    pnl_sign    = '+' if r['total_pnl'] >= 0 else ''
    emoji       = '🟢' if r['total_pnl'] >= 0 else '🔴'

    def trade_rows(trades, show_pnl=True):
        rows = ''
        for t in trades:
            pnl = t.get('pnl', 0)
            pnl_str = f"${pnl:+.2f}" if show_pnl else '⏳ pending'
            color = '#27ae60' if pnl > 0 else ('#e74c3c' if pnl < 0 else '#888')
            rows += f"""
            <tr>
              <td style='padding:6px 8px;border-bottom:1px solid #f0f0f0'>{t.get('ticker','')}</td>
              <td style='padding:6px 8px;border-bottom:1px solid #f0f0f0'>{t.get('side','').upper()}</td>
              <td style='padding:6px 8px;border-bottom:1px solid #f0f0f0'>${t.get('cost',0):.2f}</td>
              <td style='padding:6px 8px;border-bottom:1px solid #f0f0f0;color:{color};font-weight:bold'>{pnl_str}</td>
            </tr>"""
        return rows

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset='utf-8'></head>
<body style='font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f5f5;margin:0;padding:20px'>
<div style='max-width:560px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)'>

  <!-- Header -->
  <div style='background:#1a1a2e;padding:24px 28px'>
    <h1 style='margin:0;color:#fff;font-size:20px'>ClawdBot Daily Report {emoji}</h1>
    <p style='margin:4px 0 0;color:#aaa;font-size:13px'>{r['date']}</p>
  </div>

  <!-- P&L Summary -->
  <div style='padding:24px 28px;border-bottom:1px solid #f0f0f0'>
    <div style='display:flex;gap:20px;flex-wrap:wrap'>
      <div>
        <p style='margin:0;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px'>Total P&amp;L</p>
        <p style='margin:4px 0 0;font-size:32px;font-weight:700;color:{pnl_color}'>{pnl_sign}${r['total_pnl']:.2f}</p>
      </div>
      <div style='border-left:1px solid #eee;padding-left:20px'>
        <p style='margin:0;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px'>Win Rate</p>
        <p style='margin:4px 0 0;font-size:32px;font-weight:700;color:#333'>{r['win_rate']:.0f}%</p>
      </div>
      <div style='border-left:1px solid #eee;padding-left:20px'>
        <p style='margin:0;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px'>Record</p>
        <p style='margin:4px 0 0;font-size:32px;font-weight:700;color:#333'>{r['wins']}W / {r['losses']}L</p>
      </div>
    </div>
    <p style='margin:16px 0 0;font-size:13px;color:#888'>
      Wagered: ${r['total_wagered']:.2f} | Open exposure: ${r['open_exposure']:.2f}
    </p>
  </div>

  <!-- Open Positions -->
  {f"""
  <div style='padding:20px 28px;border-bottom:1px solid #f0f0f0'>
    <h3 style='margin:0 0 12px;font-size:14px;color:#333'>Open Positions ({r['open']})</h3>
    <table style='width:100%;border-collapse:collapse;font-size:13px'>
      <tr style='color:#888;font-size:11px;text-transform:uppercase'>
        <th style='text-align:left;padding:4px 8px'>Market</th>
        <th style='text-align:left;padding:4px 8px'>Side</th>
        <th style='text-align:left;padding:4px 8px'>Cost</th>
        <th style='text-align:left;padding:4px 8px'>P&L</th>
      </tr>
      {trade_rows(r['open_details'], show_pnl=False)}
    </table>
  </div>
  """ if r['open_details'] else ''}

  <!-- Settled Trades -->
  {f"""
  <div style='padding:20px 28px;border-bottom:1px solid #f0f0f0'>
    <h3 style='margin:0 0 12px;font-size:14px;color:#333'>Settled Trades</h3>
    <table style='width:100%;border-collapse:collapse;font-size:13px'>
      <tr style='color:#888;font-size:11px;text-transform:uppercase'>
        <th style='text-align:left;padding:4px 8px'>Market</th>
        <th style='text-align:left;padding:4px 8px'>Side</th>
        <th style='text-align:left;padding:4px 8px'>Cost</th>
        <th style='text-align:left;padding:4px 8px'>P&L</th>
      </tr>
      {trade_rows(r['win_details'] + r['loss_details'])}
    </table>
  </div>
  """ if r['settled'] else ''}

  <!-- Footer -->
  <div style='padding:16px 28px;background:#fafafa'>
    <p style='margin:0;font-size:12px;color:#bbb'>ClawdBot · Kelly-sized prediction market trading · Auto-generated</p>
  </div>

</div>
</body>
</html>"""
    return html


def send_report():
    trades = load_ledger()
    if not trades:
        print("No trades in ledger yet — skipping email.")
        return

    r    = build_report(trades)
    html = format_email_html(r)

    pnl_sign = '+' if r['total_pnl'] >= 0 else ''
    subject  = f"ClawdBot Daily: {pnl_sign}${r['total_pnl']:.2f} | {r['wins']}W/{r['losses']}L | {r['date']}"

    if not RESEND_API_KEY:
        print("ERROR: RESEND_API_KEY not set in .env")
        print(f"Would send: {subject}")
        return

    try:
        resp = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'from': FROM_EMAIL,
                'to':   [TO_EMAIL],
                'subject': subject,
                'html': html,
            },
            timeout=15,
        )
        data = resp.json()
        if resp.status_code == 200 or data.get('id'):
            print(f"✓ Report sent to {TO_EMAIL} (id: {data.get('id')})")
            print(f"  Subject: {subject}")
        else:
            print(f"✗ Resend error {resp.status_code}: {data}")
    except Exception as e:
        print(f"✗ Email failed: {e}")


if __name__ == '__main__':
    send_report()
