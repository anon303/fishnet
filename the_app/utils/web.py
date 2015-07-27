import requests

# from urlparse import urlparse
# from ipdb import set_trace

msg = {
    "cant_connect": "[E] The webserver did't return a valid response.\n"
                    "[*] The URL you tried: %s"
}


def is_it_up(url):
    """
    Method to check whether a website is up: the method will check whether the
    frontpage can be requested with a 200 return code. The passed-in URL is not
    checked for syntax errors; that should be enforced when creating the Shop/
    Brand instance for which this functions gets called.
    """
    try:
        response = requests.get(url)
        return response.ok
    except requests.exceptions.ConnectionError:
        print(msg["cant connect"] % url)
