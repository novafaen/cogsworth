"""Scheduler for Cogsworth.

Will schedule and handle event callbacks.
"""

from datetime import datetime, timezone
from time import localtime, strftime, sleep
import logging
from threading import Thread

from pysolar.solar import get_altitude
import schedule

# supress logging from third party library
logging.getLogger('schedule').setLevel(logging.WARNING)

log = logging.getLogger('cogsworth')


class Scheduler(Thread):
    """Scheduler handles events, in a threaded way."""

    def __init__(self, config):
        """Create and initiate ``Stick`` application."""
        Thread.__init__(self)

        self._config = config
        self._previous_sun_angle = 360  # invalid value

        log.debug('scheduler initiating')

        # add configured events to schedule
        for event in config['events']:
            name = event['name']
            days = event['days']
            if 'time' in event:
                self._schedule_onetime(name, event['time'], days)
            else:
                start = event['start']
                end = event['end']
                self._schedule_spantime(name, start, end, days)

        # add sun rise and dawn to schedule
        schedule.every().minute.do(self._sun_event)

    def _schedule_onetime(self, name, time, days):
        for day in days:
            if day == 'monday':
                schedule.every().monday.at(time).do(self._emit_event, name)
            elif day == 'tuesday':
                schedule.every().tuesday.at(time).do(self._emit_event, name)
            elif day == 'wednesday':
                schedule.every().wednesday.at(time).do(self._emit_event, name)
            elif day == 'thursday':
                schedule.every().thursday.at(time).do(self._emit_event, name)
            elif day == 'friday':
                schedule.every().friday.at(time).do(self._emit_event, name)
            elif day == 'saturday':
                schedule.every().saturday.at(time).do(self._emit_event, name)
            elif day == 'sunday':
                schedule.every().sunday.at(time).do(self._emit_event, name)

        log.debug(f'registered one time event {name}, {", ".join(days)}'
                  f' at {time}')

    def _schedule_spantime(self, name, start, end, days):
        for day in days:
            schedule.every(1).minute.do(
                self._emit_event_span,
                name, start, end,
                ['monday', 'tuesday', 'wednesday',
                 'thursday', 'friday', 'saturday', 'sunday'].index(day))

        log.debug(f'registered span time event {name}, {start}-{end}, '
                  f'for {", ".join(days)}')

    def _emit_event(self, name):
        log.debug(f'emitting event {name}')

    def _emit_event_span(self, name, start, end, day):
        if day != datetime.today().weekday():
            return  # not today, do nothing
        now = strftime("%H:%M", localtime())
        if start < end and start <= now <= end \
                or start > end and now > start > end \
                or start > end and now < end < start:
            self._emit_event(name)

    def _sun_event(self):
        now_utc = datetime.now(tz=timezone.utc)

        longitude = self._config['location']['longitude']
        latitude = self._config['location']['latitude']

        sun_angle = get_altitude(longitude, latitude, now_utc)

        if self._previous_sun_angle == 360:
            self._previous_sun_angle = sun_angle  # store first time
        else:
            if self._previous_sun_angle < 0 and sun_angle >= 0:
                self._emit_event('sun_rise')
            elif self._previous_sun_angle > 0 and sun_angle <= 0:
                self._emit_event('sun_set')

    def run(self):
        """Start the thread."""
        log.debug('Scheduler started')
        while True:
            schedule.run_pending()
            sleep(1)
