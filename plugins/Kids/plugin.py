
import calculator
reload(calculator)
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import sys,time,random,string
# from BeautifulSoupJK import BeautifulSoup
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import re


class Kids(callbacks.Plugin):
    """Some useful tools for Kids."""
    tips = 0

    _allchars = string.maketrans('','')

    def _prepare_term(self,s,keep=""):
        #return self._makefilter(string.letters+keep)(s).capitalize()
        return self._makefilter(string.letters+string.digits+keep)(s)

    def _makefilter(self,keep):
        _delchars = self._allchars.translate(self._allchars,keep)
        return lambda s,a=self._allchars,d=_delchars: s.translate(a,d)

    def __init__(self,irc):
        callbacks.Privmsg.__init__(self,irc)

    def define(self,irc,msg,args):
        """[word]
        look up the word in wordnet"""
        if len(args) != 1:
            irc.reply("you gotta give me a word to define")
            return
        word = self._prepare_term(args[0],"")
        url = 'http://wordnet.princeton.edu/perl/webwn?s=' + word
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup()
        soup.feed(html)
        maintable = soup.fetch('li')
        retdef = [] 
        checkfordefs = len(maintable)
        if checkfordefs != 0:
            for lines in maintable:
                converttostring = str(lines)
                definition = re.sub('^.*\(|\).*$', '', converttostring)
                retdef.append(definition)
        else:
            retdef.append("not found.  Is %s spelled corectly?" % word)
        irc.reply(word + ": " + "; ".join(retdef))

    def calc(self,irc,msg,args):
        """
        >>>(405 - 396) * 3
        (405-396)*3 = 27.0
        """
        s = " ".join(args).strip().replace(' ','')
        val = calculator.parse_and_calc(s)
        result = "%s = %s"%(s, val.__str__(), )
        irc.reply(result)

    def cve(self,irc,msg,args):
        word= self._prepare_term(args[0],"-")
        if re.search('cve', word, re.IGNORECASE) == None:
            url = 'http://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=' + word
            category = 'keyword'
        else:
            url = 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' +word
            category = 'name'
        # Read the URL and pass it to BeautifulSoup.
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup()
        soup.feed(html)
        cveroot = "http://cve.mitre.org"
        # Read the main table, extracting the words from the table cells.
        hreftable = soup.fetch('a', {'href':re.compile('cvename')}, limit=4)
        h1table = soup.fetch('h1')
        h1string = str(h1table)
        if category == 'keyword':
            fonttable = soup.fetch('font', limit=11)
        else:
            fonttable = soup.fetch('font', limit=17)
        if (len(fonttable) == 3) or (re.search('error', h1string, re.IGNORECASE) != None):
            irc.reply("No data found regarding " + word)
        else:
            cve = []
            href = []
            ret = ''
            for line in fonttable:
                string = str(line)
                cve.append(re.sub('^.*">|</font>|\\n', '', string))
            for line in hreftable:
                string = str(line)
                splitstring = string.split('>')
                #print splitstring
                href.append(re.sub('^.*="|"', '', splitstring[0]))
            ret =  "%s %s" % (cve[3], cve[4])
            if category == 'keyword':
                for link in href:
                    ret += cveroot + link + " "
            else:
                ret +=cve[8]
            irc.reply(ret)

Class = Kids


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=78:
