from typing import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings


def create_scheduler(job: Callable[[], Awaitable[None]]) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job,
        trigger="interval",
        # FIX (баг №5): минуты, а не секунды
        minutes=settings.parse_schedule_minutes,
        coalesce=True,
        max_instances=1,
    )
    return scheduler
