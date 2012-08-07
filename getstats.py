from urllib2 import Request, urlopen
from time import localtime, strptime, strftime, time
from datetime import date, datetime, timedelta
from json import loads, dumps
from re import findall
from os.path import exists
from os import mkdir

try:
    # maybe you don't have Jinja2?
    from jinja2 import Template
except:
    print "In order for this script to function, you need to install Jinja2 from pip"
    import sys
    sys.exit(0)

def get_stats_week(today):
    
    class ReturnRange(object):
        
        def __init__(self, start, end):
            self.start = start
            self.end = end
        
        def __str__(self):
            return dumps({'start': start.isoformat(), 'end': end.isoformat()})

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


class FormatStats(object):
    
    def __init__(self):
        raw_tpl = open("./weekly.tpl.html", 'r').read()
        self.template = Template(raw_tpl)

    def format(self, data):
        return self.template.render(data)

class GetStats(object):

    def __init__(self):
        self.bugzilla_url = 'https://api-dev.bugzilla.mozilla.org/latest/bug?product=Add-on%20SDK'
        self.range = get_stats_week(localtime())
        self.firefox_version = '14.0'
        self.link_date = strftime("%Y-%m-%d")
        self.title_date = "Jetpack Project: weekly update for " + strftime("%B %d, %Y")

    def get_fixed(self):
        """ get the number of fixed bugs for the previous whole week """
        params = 'changed_after=%s&changed_before=%s&changed_field=resolution&changed_field_to=FIXED'
        url = self._format_url(params)
        parsed = self._get(url)
        return len(parsed['bugs'])
        
    def get_new(self):
        """ get the number of newly created bugs for the previous whole week """
        params = 'changed_after=%s&changed_before=%s&'
        url = self._format_url(params) + '&changed_field=[Bug%20creation]'
        parsed = self._get(url)
        return len(parsed['bugs'])
        
    def get_open(self):
        """ get the number of current open bugs """
        params = '&status=UNCONFIRMED&status=NEW&status=ASSIGNED&status=REOPENED'
        url = "%s&%s" % (self.bugzilla_url, params)
        parsed = self._get(url)
        return len(parsed['bugs'])
        
    def get_addons_number(self):
        """scrape the AMO site for the number of current jetpack addons """
        url = "https://addons.mozilla.org/en-US/firefox/tag/jetpack?appver=%s" % self.firefox_version
        print url
        raw = urlopen(url).read()
        matches = findall('Showing [\S\s]+?of <b>([\d]+?)</b>', raw)
        return matches.pop()
        
    def get_pull_requests(self):
        """github and get the number of pull requests"""
        url = "https://github.com/mozilla/addon-sdk"
        raw = urlopen(url).read()
        matches = findall('Pull Requests <span class=\'counter\'>([\d]+?)</span>', raw)
        return matches.pop()
        
    def _format_url(self, str):
        params =  str % (self.range.start.isoformat(), self.range.end.isoformat())
        return "%s&%s" % (self.bugzilla_url, params)
    
    def _get(self, url):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        n = Request(url, None, headers)
        result = urlopen(n).read()
        return loads(result)

    def generate(self):
        print "Fetching fixed bugs..."
        fixed = self.get_fixed()
        print "Fetching new bugs..."
        new = self.get_new()
        print "Fetching open bugs..."
        open = self.get_open()
        print "Fetching total addons..."
        total_jetpacks = self.get_addons_number()
        print "Fetching pull requests..."
        pull_requests = self.get_pull_requests()
        
        run_time = strftime('%Y-%m-%d %H:%M:%S %Z')

        
        print "Formatting data..."
        data = {
            'open': open,
            'new': new,
            'fixed': fixed,
            'total_jetpacks': total_jetpacks,
            'pull_requests': pull_requests,
            'range_from': self.range.start.isoformat(),
            'range_to': self.range.end.isoformat(),
            'fx_version': self.firefox_version,
            'run_time': run_time,
            'link_date': self.link_date, 
            'title_date': self.title_date
        }
        
        fmt = FormatStats()
        print "Done!\n"
        return fmt.format(data)

if __name__ == '__main__':
    print "Generating weekly stats..."
    gs = GetStats()
    html = gs.generate()
    if not exists('./output'):
        mkdir('./output')
    open("./output/output-%s.html" % strftime('%Y-%m-%d'), 'w').write(html)

    print "\nOutput:", html


    
