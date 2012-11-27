import datetime
from atrinsic.base.choices import *

def compute_date_range(range_name,pad_end=False):
    ''' Determine a range of dates and times based on specified arguments.
        if pad_end is set, add an extra day to the date_end
        returns a tuple of the beginning and end of the date range'''
    if range_name == REPORTTIMEFRAME_TODAY:
        date_start = datetime.date.today()
        date_end = date_start + datetime.timedelta(days=1)
        
    elif range_name == REPORTTIMEFRAME_YESTERDAY:
        date_start = datetime.date.today() - datetime.timedelta(0,3600*24,0)
        date_end = datetime.date.today()
        
    elif range_name == REPORTTIMEFRAME_PAST7DAYS:
        date_start = datetime.date.today() - datetime.timedelta(0,3600*24*7,0)
        date_end = datetime.date.today() - datetime.timedelta(0,3600*24,0)
    elif range_name == REPORTTIMEFRAME_MONTHTODATE:
        date_start = datetime.date(datetime.date.today().year,datetime.date.today().month,1)
        date_end = datetime.date.today()
        
    elif range_name == REPORTTIMEFRAME_YEARTODATE:
        date_start = datetime.date(datetime.date.today().year,1,1)
        date_end = datetime.date.today()
    elif range_name == REPORTTIMEFRAME_QUARTERTODATE:
        date_start = datetime.date(datetime.date.today().year,(datetime.date.today().month/3)*3+1,1)
        date_end = datetime.date.today()
    elif range_name == REPORTTIMEFRAME_PAST30DAYS:
        date_start = datetime.date.today() - datetime.timedelta(0,3600*24*30,0)
        date_end = datetime.date.today() - datetime.timedelta(0,3600*24,0)
    elif range_name == REPORTTIMEFRAME_LASTFULLMONTH:
        date_start = datetime.date((datetime.date.today() - datetime.timedelta(0,3600*24*32)).year,(datetime.date.today() - datetime.timedelta(0,3600*24*32)).month,1)
        date_end = date_start + datetime.timedelta(0,3600*24*(days_in_month(date_start)-1),0)
    elif range_name == REPORTTIMEFRAME_LASTFULLQUARTER:
        beginning_of_current_quarter = datetime.date(datetime.date.today().year,(datetime.date.today().month/3)*3+1,1)
        sometime_in_last_quarter = beginning_of_current_quarter- datetime.timedelta(0,24*3600*2)
        end_of_last_quarter = datetime.date(sometime_in_last_quarter.year,sometime_in_last_quarter.month,days_in_month(sometime_in_last_quarter))

        # subtract 65 days from end_of_last_quarter, and get the first day of that month
        sometime_first_month_of_quarter = end_of_last_quarter - datetime.timedelta(0,24*3600*65,0)
        first_of_quarter = datetime.date(sometime_first_month_of_quarter.year,
                                         sometime_first_month_of_quarter.month,
                                         1)

        date_start = first_of_quarter
        date_end = end_of_last_quarter
    elif range_name == REPORTTIMEFRAME_PAST365DAYS:
        date_start = datetime.date.today() - datetime.timedelta(0,3600*24*365,0)
        date_end = datetime.date.today() - datetime.timedelta(0,3600*24,0)
    elif range_name == REPORTTIMEFRAME_LASTFULLYEAR:
        date_start = datetime.date(datetime.date.today().year-1,1,1)
        date_end = datetime.date(datetime.date.today().year-1,12,31)
    else:
        return compute_date_range(REPORTTIMEFRAME_TODAY)

    if pad_end:
        date_end = date_end + datetime.timedelta(0,3600*24,0)
        
     
 
    return date_start,date_end


def days_in_month(d):
    ''' Returns the number of days in a specified month '''

    if d.month == 2:
        if d.year % 4 == 0:
            if d.year % 400 == 0:
                return 29
        else:
            return 28
    if d.month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    else:
        return 30
