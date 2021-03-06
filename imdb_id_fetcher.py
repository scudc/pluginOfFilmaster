# encoding: utf-8 
#-------------------------------------------------------------------------------
# Filmaster - a social web network and recommendation engine
# Copyright (c) 2009 Filmaster (Borys Musielak, Adam Zielinski).
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import urllib2
try:
    from settings import *
except:
    IDS_LIST_FILE = "ids_list.txt"   
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
from httplib2 import socks
from datetime import date,datetime,timedelta
import re
import sys
import getopt
def parse(movies_html,file):
    soup = BeautifulSoup(movies_html)
    tables = soup.findAll("table", attrs={"class" : "results"})
    links = soup.find("span",{"class" : "pagination"}).findAll('a')
    next_url = None
    for link in links: 
        if "Next&nbsp;&raquo;" == link.string:
            next_url = link['href']
            break
    for div in tables:
#        div = str(div)
#        firstLine = re.match('.*<a href="/title/tt(\d+)/">.*', div)
#        print firstLine.group(1).strip()
#        for line in div:
#            line = str(line)
#            line = line.replace("\n", "")
        for line in div:
            line = str(line)
            line = line.replace("\n", "")
            if re.match('<h5>.*</h5>*', line):
                pass
            elif re.match('(.*)<a href="/title/tt(\d+)/">.*', line):
                firstLine = re.match('(.*)<a href="/title/tt(\d+)/">.*', line)
                if firstLine != None:
                    imdbid = firstLine.group(2).strip()
                    print imdbid
                    file.write(imdbid + '\n')
    return next_url

#get the html from url
def get_html_by_url(url) :
    moves_html = None
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded');
    req.add_header('Cache-Control', 'no-cache');
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8');
    req.add_header('Connection', 'Keep-Alive')
    try:
        movies_html = urllib2.urlopen(req).read()
    except IOError:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 8080)
        socks.wrapmodule(urllib2)
        movies_html = urllib2.urlopen(req).read()
    return movies_html

def main():
    HELP = """
  usage : 
        -a "Get All imdbid"
        -i num "Get the lastest num day update imdbid"
        -d path/to/store/imdbids
    """
    options,arguments = getopt.getopt(sys.argv[1:],"au:d:")
    opts = dict(options)

    baseUrl = "http://www.imdb.com"
    allUrl = "/search/title?title_type=video_movie,movie,tv_movie,tv_mini_series,tv_mini-series,tv&count=100&release_date=1500-11-01"
    updateUrl = "/search/title?title_type=video_movie,movie,tv_movie,tv_mini_series,tv_mini-series,tv&count=100&release_date="
    today = datetime.today()
    currDate = date(today.year,today.month,today.day).isoformat()
    idsFilePath = ""
    if "-a" not in opts and "-u" not in opts and "-d" not in opts :
        print HELP
        exit(1)
    if "-a" in opts and "-u" in opts:
        print "-a and -u are conflict"
        print HELP
        exit(1)
    if "-u" in opts :
        num = opts.get('-u','').replace('"',"")
        updateDate = (date.today() - timedelta(int(num))).isoformat()
        imdbUrl = baseUrl + updateUrl + updateDate + "," + currDate
    if "-a" in opts :
        imdbUrl = baseUrl + allUrl + "," + currDate
    if "-d" in opts :
        idsFilePath =  opts.get('-d','').replace('"',"")
    try:
        file = open(idsFilePath+IDS_LIST_FILE, 'w')
        movies_html = get_html_by_url(imdbUrl)
        next_url = parse(movies_html,file)
        while next_url != None:
            next_url = baseUrl + next_url
            movies_html = get_html_by_url(next_url)
            next_url = parse(movies_html,file)
        file.close()
    except IOError:
        print "Could not get %s" % imdbUrl
        sys.exit(2)

if __name__ == "__main__":
    main()
