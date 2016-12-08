import csv
import urllib.request
import requests
import datetime
import time
import logging
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger('parsedatetime')

from flask import redirect, render_template, request, session, url_for
from functools import wraps

# for embedContentHelper
from urllib.parse import urlparse, parse_qs

def page_error(error_text=""):
    """Renders message as a page_error to user."""
    
    return render_template("error.html", error=error_text)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function
    
def embedContentHelper(embedContent):
    
    # for parsing image URLs
    imageFormatList = [".jpg", ".png", ".gif", ".jpeg", ".tiff"]

    # first check if the embedContent URL exists
    request = requests.get(embedContent)
    if request.status_code != 200:
        return "embedBroken"
        
    else:    
        # then parse for YouTube
        if "youtube" in embedContent:
            # get videoID from URL
            URL = urlparse(embedContent)
            videoID = parse_qs(URL.query)
            
            # prepare source
            src = "https://www.youtube.com/embed/" + videoID["v"][0]
            
            # create embed HTML
            embedHTML = "<div class=\"embedContentVideo\"><iframe src=\"" + src + "\" frameborder=\"0\" allowfullscreen></iframe></div>"
            
        # then parse for Images
        elif any(extension in embedContent for extension in imageFormatList):
            
            # prepare source
            src = embedContent
            
            # create embed HTML
            embedHTML = "<img src=\"" + src + "\" width=\"100%\" class=\"embedContentImage\">"
        
        # then parse for all other content
        else:
            
            embedHTML = "<a target=\"_blank\" href=\""+ embedContent + "\"><h3>" + embedContent + "</h3></a>"
            
        ### return embedHTML for all cases
        return embedHTML
        
#########################################################################################################

def makeEpochTime(date_time):
    """
    provides the seconds since epoch give a python datetime object.
    
    @param date_time: Python datetime object

    @return:
        seconds_since_epoch:: int 
    """
    date_time = date_time.isoformat().split('.')[0].replace('T',' ')
    #'2009-07-04 18:30:47'
    pattern = '%Y-%m-%d %H:%M:%S'
    seconds_since_epoch = int(time.mktime(time.strptime(date_time, pattern)))
    return seconds_since_epoch 

def convertToHumanReadable(date_time):
    """
    converts a python datetime object to the 
    format "X days, Y hours ago"

    @param date_time: Python datetime object

    @return:
        fancy datetime:: string
    """
    current_datetime = datetime.datetime.now()
    delta = str(current_datetime - date_time)
    if delta.find(',') > 0:
        days, hours = delta.split(',')
        days = int(days.split()[0].strip())
        hours, minutes = hours.split(':')[0:2]
    else:
        hours, minutes = delta.split(':')[0:2]
        days = 0
    days, hours, minutes = int(days), int(hours), int(minutes)
    datelets =[]
    years, months, xdays = None, None, None
    plural = lambda x: 's' if x!=1 else ''
    if days >= 365:
        years = int(days/365)
        datelets.append('%d year%s' % (years, plural(years)))
        days = days%365
    if days >= 30 and days < 365:
        months = int(days/30)
        datelets.append('%d month%s' % (months, plural(months)))        
        days = days%30
    if not years and days > 0 and days < 30:
        xdays =days
        datelets.append('%d day%s' % (xdays, plural(xdays)))        
    if not (months or years) and hours != 0:
        datelets.append('%d hour%s' % (hours, plural(hours)))        
    if not (xdays or months or years):
        datelets.append('%d minute%s' % (minutes, plural(minutes)))        
    return ' '.join(datelets) + ' ago'
    

def makeFancyDatetime(req_datetime):
    """
    a consolidate method to provide a nice output 
    taken from the other two methods as a dictionary,
    easily convertible to json.
    
    @param req_datetime: python datetime object
    
    @return:
        Python dictionay object with two key, value pairs
        representing 'fancy_datetime' and 'seconds_since_epoch'
    """
    return {'fancy_datetime': convertToHumanReadable(req_datetime), 
            'seconds_since_epoch': makeEpochTime(req_datetime)
            }