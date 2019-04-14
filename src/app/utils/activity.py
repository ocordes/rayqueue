"""

app/utils/activity.py

written by: Oliver Cordes 2019-04-12
changed by: Oliver Cordes 2019-04-14


"""

from datetime import datetime

from flask import current_app

from app import db

from app.models import DayActivity



class Activity(object):
    def __init__(self, db):
        self._db = db


    """
    _check_init

    loads the data for the total statistics, if no data is available
    create a new empty dataset, which has the id=0!
    """
    def _check_init(self):
        if DayActivity.query.count() == 0:
            current_app.logger.info('Create data for the total statistics')
            total = DayActivity(date='')
            self._db.session.add(total)
            self._db.session.commit()
        else:
            #current_app.logger.info('Load data for the total statistics')
            total = DayActivity.query.get(1)

        return total


    def _today_strdate(self):
        return datetime.utcnow().strftime('%Y-%m-%d')

    """
    _today_data

    returns the data set corresponding to the current date, if no
    data is available create a dataset
    """
    def _today_data(self):
        date = self._today_strdate()

        #current_app.logger.info('Load data for today\'s statistics')
        today = DayActivity.query.filter_by(date=date).first()

        if today is None:
            current_app.logger.info('Create data for today\'s statistics')
            today = DayActivity(date=date)
            self._db.session.add(today)
            self._db.session.commit()

        return today


    def get_total_images(self):
        total = self._check_init()

        if total is not None:
            return total.stat_total_images
        else:
            return 0


    def get_total_errors(self):
        total = self._check_init()

        if total is not None:
            return total.stat_total_errors
        else:
            return 0


    def get_total_submits(self):
        total = self._check_init()

        if total is not None:
            return total.stat_total_submits
        else:
            return 0


    def get_total_render_time(self):
        total = self._check_init()

        if total is not None:
            return total.stat_render_time
        else:
            return 0


    def get_today_images(self):
        today = self._today_data()

        if today is not None:
            return today.stat_total_images
        else:
            return 0


    def get_today_errors(self):
        today = self._today_data()

        if today is not None:
            return today.stat_total_errors
        else:
            return 0


    def get_today_submits(self):
        today = self._today_data()

        if today is not None:
            return today.stat_total_submits
        else:
            return 0


    def get_today_render_time(self):
        today = self._today_data()

        if today is not None:
            return today.stat_render_time
        else:
            return 0


    """
    add_submit

    adds one image to the submits entries
    """
    def add_submit(self):
        today = self._today_data()
        if today is not None:
            today.stat_total_submits += 1

        total = self._check_init()
        if total is not None:
            total.stat_total_submits += 1

        self._db.session.commit()


    """
    add_image

    adds one image to the totals entries, take into account the
    error status and rendering time!
    """
    def add_image(self, error=False, render_time=0):
        today = self._today_data()
        if today is not None:
            today.stat_total_images += 1
            if error:
                today.stat_total_errors += 1
            today.stat_render_time += render_time

        total = self._check_init()
        if total is not None:
            total.stat_total_images += 1
            if error:
                total.stat_total_errors += 1
            total.stat_render_time += render_time

        self._db.session.commit()
