from time import localtime, strptime, strftime, time
from datetime import date, datetime, timedelta
from simplejson import loads, dumps

def get_stats_week(date_string):
    
    class ReturnRange(object):
        
        def __init__(self, start, end):
            self.start = start
            self.end = end
        
        def __str__(self):
            return dumps({'start': start.isoformat(), 'end': end.isoformat()})
            
    
    today = strptime(date_string, '%Y-%m-%d')
    date_today = date(today[0], today[1], today[2])
    # Tuesday is 1
    day_of_week = date_today.weekday()
    #print "day of week is: %s" % day_of_week
    if day_of_week == 1:
        # date range is previous monday until today
        start = date_today - timedelta(days=8)
        end = date_today
    elif day_of_week == 0:
        # date range is from two weeks ago until previous tuesday
        start = date_today - timedelta(days=14)
        end = date_today - timedelta(days=6)
    else:
        # date range is from monday-before-last until previous tuesday
        diff = day_of_week - 1
        end = date_today - timedelta(days=diff)
        start = end - timedelta(days=8)
    return ReturnRange(start, end)

if __name__ == '__main__':
    print "running some tests..."

    # test: an actual tuesday
    print get_stats_week('2011-11-22')
    
    # test: a monday
    print get_stats_week('2011-11-21')
    
    # test: any other day
    print get_stats_week('2011-11-25') # actually a friday
    
    # test: a month boundary
    print get_stats_week('2011-11-3')




