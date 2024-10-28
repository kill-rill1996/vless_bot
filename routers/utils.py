import datetime

import pytz


async def convert_to_datetime_from_unix(unix_time: int) -> datetime:
    """Перевод unix time в формат ДД.ММ.ГГГГ"""
    timezone = pytz.timezone('Europe/Moscow')
    return datetime.datetime.fromtimestamp(unix_time / 1000, tz=timezone).date().strftime("%d.%m.%Y")

