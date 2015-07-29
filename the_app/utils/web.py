import BeautifulSoup
import requests
import urllib
import sys

# from urlparse import urlparse
# from ipdb import set_trace

msg = {
    "cant_connect": "[E] The webserver did't return a valid response.\n"
                    "[*] The URL you tried: %s"
}


def is_it_up(url):
    """
    Function to check whether a website is up: the method will check whether th
    frontpage can be requested with a 200 return code. The passed-in URL is not
    checked for syntax errors; that should be enforced when creating the Shop/
    Brand instance for which this functions gets called.
    """
    try:
        response = requests.get(url)
        return response.ok
    except requests.exceptions.ConnectionError:
        print(msg["cant connect"] % url)


def get_full_soup(url):
    try:
        full_html = urllib.urlopen(url)
    except IOError as err:
        print("[E] Couldn't reach URL: %s" % url)
        print("[*] The error message: '%s'" % err)
        sys.exit(-1)
    else:
        full_soup = BeautifulSoup.BeautifulSoup(full_html)
        return full_soup
