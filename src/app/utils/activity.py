"""

app/utils/activity.py

written by: Oliver Cordes 2019-04-12
changed by: Oliver Cordes 2020-03-29


"""

from datetime import datetime, timedelta

from flask import current_app

from app import db

from app.models import DayActivity



class Activity(object):
    def __init__(self, db):
        self._db = db


    """
    _check_init

    create a new empty dataset is database is empty,
    this is always teh first dataset and has the id=1!
    """
    def _check_init(self):
        if DayActivity.query.count() == 0:
            current_app.logger.info('Create data for the total statistics')
            total = DayActivity(date='total')
            self._db.session.add(total)
            self._db.session.commit()


    def _today_strdate(self):
        return datetime.utcnow().strftime('%Y-%m-%d')


    def _month_strdate(self):
        return datetime.utcnow().strftime('%Y-%m')


    """
    _total_data

    returns the total data set
    """
    def _total_data(self):
        self._check_init()
        return DayActivity.query.get(1)


    """
    _today_data

    returns the data set corresponding to the current date, if no
    data is available create a dataset
    """
    def _today_data(self):
        self._check_init()
        date = self._today_strdate()

        #current_app.logger.info('Load data for today\'s statistics')
        today = DayActivity.query.filter_by(date=date).first()

        if today is None:
            current_app.logger.info('Create data for today\'s statistics')
            today = DayActivity(date=date)
            self._db.session.add(today)
            self._db.session.commit()

        return today


    def _month_data(self, sdate):
        month = DayActivity.query.filter_by(date=sdate).first()
        if month is None:
            current_app.logger.info('Month data for %s not available, repairing database!' % sdate)

            # User.query.filter(User.email.endswith('@example.com')).all()

            sdate2 = sdate + '-'
            daylist = DayActivity.query.filter(DayActivity.date.startswith(sdate2)).all()

            month = DayActivity(date=sdate)
            month.stat_total_images = 0
            month.stat_total_errors = 0
            month.stat_total_submits = 0

            for day in daylist:
                month.stat_total_images += day.stat_total_images
                month.stat_total_errors += day.stat_total_errors
                month.stat_total_submits += day.stat_total_submits
                # handle the initial render time differently
                if month.stat_render_time is None:
                    month.stat_render_time = day.stat_render_time
                else:
                    month.stat_render_time += day.stat_render_time


            self._db.session.add(month)
            self._db.session.commit()

        return month


    """
    """
    def _today_month_data(self):
        date = self._month_strdate()
        return self._month_data(date)


    """
    get_month_stats

    return the data for a specific month, the data should be available,
    otherwise repair the database
    """
    def get_month_stats(self, date):
        stats = self._month_data(date)
        if stats is None:
            val = 0
            err = 0
        else:
            val = stats.stat_total_images
            err = stats.stat_total_errors

        return val, err


    """
    get_day_stats

    returns the data for a specific date, if available, otherwise 0,0
    """
    def get_day_stats(self, date):
        stats = DayActivity.query.filter_by(date=date).first()
        if stats is None:
            val = 0
            err = 0
        else:
            val = stats.stat_total_images
            err = stats.stat_total_errors
        return val, err


    def get_total_images(self):
        total = self._total_data()

        if total is not None:
            return total.stat_total_images
        else:
            return 0


    def get_total_errors(self):
        total = self._total_data()

        if total is not None:
            return total.stat_total_errors
        else:
            return 0


    def get_total_submits(self):
        total = self._total_data()

        if total is not None:
            return total.stat_total_submits
        else:
            return 0


    def get_total_render_time(self):
        total = self._total_data()

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

        total = self._total_data()
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

        month = self._today_month_data()
        if month is not None:
            month.stat_total_images += 1
            if error:
                month.stat_total_errors += 1
            month.stat_render_time += render_time

        total = self._total_data()
        if total is not None:
            total.stat_total_images += 1
            if error:
                total.stat_total_errors += 1
            total.stat_render_time += render_time

        self._db.session.commit()
