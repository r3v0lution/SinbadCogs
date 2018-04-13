from datetime import datetime, timedelta


class AntiSpam:
    """
    Because people are jackasses
    """

    def __init__(self):
        self.event_timestamps = []

    def _interval_check(self, interval: timedelta, threshold: int) -> bool:
        return len(
            [t for t in self.event_timestamps
             if (t + interval) > datetime.utcnow()]
        ) >= threshold

    @property
    def spammy(self) -> bool:
        return self._interval_check(timedelta(seconds=5), 3) \
            or self._interval_check(timedelta(minutes=1), 5) \
            or self._interval_check(timedelta(hours=1), 30)

    def stamp(self) -> None:
        self.event_timestamps.append(datetime.utcnow())
        # This is to avoid people abusing the bot to get
        # it ratelimited. We don't care about anything older than
        # 1 hour, so we can discard those events
        self.event_timestamps = [
            t for t in self.event_timestamps
            if t + timedelta(hours=1) > datetime.utcnow()
        ]
