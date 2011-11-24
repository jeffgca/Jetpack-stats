# Jetpack Stats

_This is a quick script to generate the 'quick stats' section of the jetpack weekly
post._

__Requirements:__

* python, simplejson
* jinja2 ( `pip install Jinja2` )

To use:

    git clone git://github.com/canuckistani/Jetpack-stats.git
    cd Jetpack-stats
    python getstats.py

Sample output:

    Generating weekly stats...
    Fetching fixed bugs...
    Fetching new bugs...
    Fetching open bugs...
    Fetching total addons...
    Fetching pull requests...
    Formatting data...
    Done!
    
The script outputs an html file called 'output-YYYY-MM-DD.html' in the current
folder containing an html fragment suitable for posting to the AMO blog.
