"""
scheduler.py - Scheduled task runner for the Kalshi bot
"""

import schedule
import time
import asyncio
import logging

logger = logging.getLogger("kalshi.scheduler")


def run_scheduler(bot):
    """
    Set up and run the scheduler indefinitely.
    bot: KalshiBot instance
    """

    def _run_async(coro):
        asyncio.run(coro)

    # Full scan + execute daily at 8am
    schedule.every().day.at("08:00").do(lambda: _run_async(bot.run_full_loop()))

    # Monitor positions every 6 hours
    schedule.every(6).hours.do(lambda: _run_async(bot.monitor_positions()))

    # Check unfilled orders every 2 hours
    schedule.every(2).hours.do(lambda: _run_async(bot.check_unfilled_orders()))

    # Weekly report every Monday at 6am
    schedule.every().monday.at("06:00").do(lambda: _run_async(bot.generate_weekly_report()))

    logger.info("Scheduler running. Press Ctrl+C to stop.")
    logger.info("  - Full scan + execute: daily at 08:00")
    logger.info("  - Position monitor:    every 6 hours")
    logger.info("  - Order check:         every 2 hours")
    logger.info("  - Weekly report:       Monday 06:00")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
