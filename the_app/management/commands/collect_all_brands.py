# imports 1/3: Django-agnostic python #########################################

import BeautifulSoup
import urllib
import sys


# imports 2/3: Django #########################################################

from django.core.management.base import BaseCommand, CommandError


# imports 3/3: DIY ############################################################

from the_app import settings
from the_app.models import Brand
from the_app.utils import strings


# human-readable info #########################################################

msg = {
    "help":
        "Collect all available eurorack manufacterers, as found on "
        "modulargrid. With this you van update the Brand model known to the "
        "application.",
    "database_count":
        "[*] Currently, there are %i Brand instances(s) in our database.\n"
        "[!] Fetching all known eurorack manufacturers via URL: "
        + settings.MODULAR_GRID_URL + "...",
    "new_count":
        "[*] From the %i brand name(s) found, %i name(s) are both permitted "
        "and currently do not have a corresponding database entry.",
    "no_brand_names_in_response":
        "[E] Could not extract brand names from HTML. Aborting...",
    "write_to_instance":
        "[?] Would you like to convert the name '%s' to a new "
        "database entry? [n]/y/a(llow-all)/q(uit) >>> ",
    "skip_create":
        "[+] OK, skip creating new Brand instance for name '%s'",
    "ok_create":
        "[*] Converting this name to a new Brand instance..",
    "allow_all":
        "[!] Converting this and the %i other name(s) to Brand instances...",
    "no_new_brands":
        "[*] No new brand names were found on modulargrid.net",
    "abort":
        "[*] Aborting further execution (%i brand(s) in database).\n",
    "has_been_created":
        "[+] OK, created a Brand named: '%s'",
    "modulargrid_unreachable":
        "[E] Oops! There was an IOError while fetching data from "
        "modulargrid.net: %s",
    "invalid_choice":
        "[E] Your choice '%s' is invalid. Valid choices are: y(es) | n(o) "
        "| a(llow-all) | q(uit).\n"
}


# exposed code ################################################################

class Command(BaseCommand):
    help = msg["help"]

    def add_arguments(self, parser):
        pass

    @staticmethod
    def soup_to_brand_names(soup):
        options = soup.find(id="SearchVendor").findAll("option")
        if options == []:
            raise CommandError(msg["no_brand_names_in_response"])
        names = [n for n in [opt.getText() for opt in options] if n != '-']
        return names

    @staticmethod
    def get_full_soup():
        try:
            full_html = urllib.urlopen(settings.MODULAR_GRID_URL)
        except IOError as err:
            p('modulargrid_unreachable', err)
            abort(-1)
        else:
            full_soup = BeautifulSoup.BeautifulSoup(full_html)
            return full_soup

    @staticmethod
    def select_new_brands(all_brand_names):
        old_brand_names = [n['name'].lower() for n in
                           Brand.objects.values('name')]
        unwanted_brand_names = old_brand_names + settings.INVALID_BRAND_NAMES
        new_brand_names = [n for n in all_brand_names
                           if not n.lower() in unwanted_brand_names]
        return new_brand_names

    def handle(self, *args, **options):
        old_brand_names_count = Brand.objects.count()
        p("database_count", old_brand_names_count)
        all_brand_names = Command.soup_to_brand_names(Command.get_full_soup())
        new_brand_names = Command.select_new_brands(all_brand_names)

        if len(new_brand_names):
            p("new_count", len(all_brand_names), len(new_brand_names))
            interactive_mode = True
            for i, new_brand_name in enumerate(new_brand_names):
                if interactive_mode:
                    question = msg["write_to_instance"] % new_brand_name
                    raw_ans = raw_input(question)
                    ans = raw_ans[0].lower() if raw_ans else 'n'
                    if ans == 'a':
                        p('allow_all', len(new_brand_names) - i - 1)
                        interactive_mode = False
                    elif ans == 'q':
                        abort()
                    elif ans == 'n':
                        p('skip_create', new_brand_name)
                        continue
                    elif ans == 'y':
                        p('ok_create')
                    else:
                        p('invalid_choice', raw_ans)

                new_brand = Brand.objects.create(
                    name=new_brand_name,
                    slug=strings.sluggify(new_brand_name))
                p('has_been_created', new_brand.name)

            abort()
        else:
            p("no_new_brands")
            abort()


# local helper functions ######################################################

def p(key, *args):
    print(msg[key] % tuple(args))


def abort(statuscode=0):
    p('abort', Brand.objects.count())
    sys.exit(statuscode)
