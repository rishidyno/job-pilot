"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — Telegram Notification Service                        ║
║                                                                   ║
║  Sends real-time notifications via Telegram when:                 ║
║  - A high-match job is found (score >= threshold)                ║
║  - An application is auto-submitted                               ║
║  - An application status changes                                  ║
║  - Scraping errors occur                                          ║
║                                                                   ║
║  SETUP:                                                           ║
║  1. Message @BotFather on Telegram → create a bot → get token    ║
║  2. Message @userinfobot → get your chat ID                      ║
║  3. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env          ║
║                                                                   ║
║  USAGE:                                                           ║
║    from services.telegram_service import telegram_service          ║
║    await telegram_service.notify_new_job(job)                     ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from typing import Optional
from config import settings
from utils.logger import logger


class TelegramService:
    """
    Sends formatted notifications to Telegram.
    
    Uses the python-telegram-bot library for API communication.
    All notifications are sent to the chat ID configured in .env.
    
    Messages are formatted with Markdown for readability.
    """

    def __init__(self):
        """Initialize the Telegram bot (lazy — only when first message is sent)."""
        self._bot = None

    async def _get_bot(self):
        """
        Lazy-initialize the Telegram bot.
        
        We don't create the bot at import time because:
        1. The token might not be configured yet
        2. We want to fail gracefully if Telegram isn't set up
        """
        if self._bot is None and settings.telegram_enabled:
            try:
                from telegram import Bot
                self._bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram bot: {e}")
        return self._bot

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a text message to the configured Telegram chat.
        
        Args:
            text: Message text (supports Markdown formatting)
            parse_mode: "Markdown" or "HTML"
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not settings.telegram_enabled:
            logger.debug("Telegram not configured — skipping notification")
            return False

        try:
            bot = await self._get_bot()
            if bot:
                await bot.send_message(
                    chat_id=settings.TELEGRAM_CHAT_ID,
                    text=text,
                    parse_mode=parse_mode,
                )
                return True
        except Exception as e:
            logger.warning(f"Telegram notification failed: {e}")
        return False

    async def notify_new_job(
        self,
        title: str,
        company: str,
        location: str,
        match_score: int,
        url: str,
        portal: str,
    ) -> bool:
        """
        Send notification for a new high-match job.
        
        Args:
            title: Job title
            company: Company name
            location: Job location
            match_score: AI match score (0-100)
            url: Direct link to the job posting
            portal: Source portal name
        """
        # Emoji based on score
        if match_score >= 90:
            emoji = "🔥"
        elif match_score >= 75:
            emoji = "⭐"
        else:
            emoji = "📋"

        message = (
            f"{emoji} *New Job Match — {match_score}/100*\n\n"
            f"*{title}*\n"
            f"🏢 {company}\n"
            f"📍 {location or 'Not specified'}\n"
            f"🌐 {portal.capitalize()}\n\n"
            f"[View Job]({url})"
        )

        return await self.send_message(message)

    async def notify_application_submitted(
        self,
        title: str,
        company: str,
        portal: str,
        mode: str,
    ) -> bool:
        """Send notification when an application is submitted."""
        mode_emoji = "🤖" if mode == "auto" else "👆"
        message = (
            f"✅ *Application Submitted* {mode_emoji}\n\n"
            f"*{title}* at *{company}*\n"
            f"Via: {portal.capitalize()} ({mode} mode)"
        )
        return await self.send_message(message)

    async def notify_application_failed(
        self,
        title: str,
        company: str,
        error: str,
    ) -> bool:
        """Send notification when an auto-apply fails."""
        message = (
            f"❌ *Application Failed*\n\n"
            f"*{title}* at *{company}*\n"
            f"Error: {error[:200]}"
        )
        return await self.send_message(message)

    async def notify_scrape_complete(
        self,
        portal: str,
        jobs_found: int,
        new_jobs: int,
        high_matches: int,
    ) -> bool:
        """Send notification after a scraping run completes."""
        if new_jobs == 0:
            return False  # Don't spam when nothing new

        message = (
            f"🔍 *Scrape Complete — {portal.capitalize()}*\n\n"
            f"Found: {jobs_found} jobs\n"
            f"New: {new_jobs} jobs\n"
            f"High matches (≥{settings.MIN_MATCH_SCORE_TO_APPLY}): {high_matches}"
        )
        return await self.send_message(message)

    async def notify_daily_summary(
        self,
        total_jobs: int,
        new_today: int,
        applied_today: int,
        high_matches: int,
    ) -> bool:
        """Send a daily activity summary."""
        message = (
            f"📊 *Daily Summary*\n\n"
            f"Total jobs tracked: {total_jobs}\n"
            f"New today: {new_today}\n"
            f"Applied today: {applied_today}\n"
            f"High matches pending: {high_matches}"
        )
        return await self.send_message(message)


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
telegram_service = TelegramService()
