from pywik.PyWik import PyWik, TableWidget, ChartWidget
from django.utils import dateformat
from atrinsic import settings
def prep_date(date):
    import datetime
    if date == "month":
        right_now = datetime.datetime.now()
        thisMonth = datetime.datetime(right_now.year,right_now.month,1)#make a datetime obj for 1st of this month
        delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
        last_day = thisMonth - delta #last day of last month
        if last_day.day < right_now.day:
            final_day = last_day.day
        else:
            final_day=right_now.day
        #all this is to have a valid month span for dates, basicly from a month ago(validated) to now		
        #return str(datetime.date(right_now.year,right_now.month-1,final_day))+','+str(datetime.date(right_now.year,right_now.month,right_now.day))
        sDate = dateformat.format(datetime.date(right_now.year,right_now.month-1,final_day), settings.DATE_FORMAT)
        eDate = dateformat.format(datetime.date(right_now.year,right_now.month,right_now.day), settings.DATE_FORMAT)		
        return str(sDate)+","+str(eDate)
    elif (date == "day") | (date == "yesterday"):
        right_now = datetime.datetime.now()
        yesterday = right_now.day-1
        if yesterday == 0:
            thisMonth = datetime.date(right_now.year,right_now.month,1)#make a datetime obj for 1st of this month
            delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
            last_month = thisMonth - delta #last day of last month
            return str(datetime.date(last_month.year,last_month.month, last_month.day))+","+str(datetime.date(last_month.year,last_month.month, last_month.day))
        else:
            sDate = dateformat.format(datetime.date(right_now.year,right_now.month, yesterday), settings.DATE_FORMAT)
            eDate = dateformat.format(datetime.date(right_now.year,right_now.month, yesterday), settings.DATE_FORMAT)
            return str(sDate)+","+str(eDate)
    try:
        x = str(date.split(","))
    except:
        date = str(date)+","+str(date)
    return str(date)