from urllib2 import Request, urlopen
from time import localtime, strptime, strftime, time
from datetime import date, datetime, timedelta
from simplejson import loads, dumps
from re import findall

from date_hack import get_stats_week

try:
    # maybe you don't have Jinja2?
    from jinja2 import Template
except:
    print "In order for this script to function, you need to install Jinja2 from pip"
    import sys
    sys.exit(0)
    

class FormatStats(object):
    
    def __init__(self):
        raw_tpl = """
<h3>Quick Stats</h3>
<ul>
    <li>Total <a href="https://bugzilla.mozilla.org/buglist.cgi?bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&product=Add-on%20SDK&known_name=Jetpack-Open" target="_blank">open bugs</a>: {{ open }}</li>
    <li>Bugs <a href="https://bugzilla.mozilla.org/buglist.cgi?chfieldto={{ range_to }}&chfield=[Bug%20creation]&chfieldfrom={{ range_from }}&product=Add-on%20SDK" target="_blank">created last week</a>: {{ new }}</li>
    <li>Bugs <a href="https://bugzilla.mozilla.org/buglist.cgi?chfieldto={{ range_to }}&chfield=resolution&chfieldfrom={{ range_from }}&chfieldvalue=FIXED&product=Add-on%20SDK" target="_blank">fixed last week</a>: {{ fixed }}</li>
    <li>Total SDK-based Addons <a href="https://addons.mozilla.org/en-US/firefox/tag/jetpack?appver={{ fx_version }}" target="_blank">on AMO</a>: {{ total_jetpacks }}</li>
    <li>Open <a href="https://github.com/mozilla/addon-sdk/pulls" target="_blank">pull requests</a> on Github: {{ pull_requests }}</li>
</ul>

<em style="font-size: 85%;">Note: the stats above are based on the queries I linked to for each item. If you have suggestions on how these queries might be made more accurate,please comment below. Stats generated at {{ run_time }}</em>
"""
        self.template = Template(raw_tpl)

    def format(self, data):
        return self.template.render(data)

class GetStats(object):

    def __init__(self):
        self.bugzilla_url = 'https://api-dev.bugzilla.mozilla.org/latest/bug?product=Add-on%20SDK'
        lt = localtime()
        today = date(lt[0], lt[1], lt[2])
        self.range = get_stats_week(str(today))
        self.firefox_version = '8.0.1'

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
        url = "https://addons.mozilla.org/en-US/firefox/tag/jetpack?appver=8.0"
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
            'run_time': run_time
        }
        
        fmt = FormatStats()
        print "Done!\n"
        return fmt.format(data)

if __name__ == '__main__':
    print "Generating weekly stats..."
    gs = GetStats()
    html = gs.generate()
    open("./output-%s.html" % strftime('%Y-%m-%d'), 'w').write(html)
    
