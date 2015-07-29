# -*- coding: UTF-8 -*-

# imports 1/3: Django-agnostic python #########################################

import BeautifulSoup
import urlparse
import urllib
import time
import sys

from ipdb import set_trace
from time import sleep

# imports 2/3: Django #########################################################

from django.core.management.base import BaseCommand
# from django.core.management.base import CommandError


# imports 3/3: DIY ############################################################

from the_app import settings
from the_app.models import Brand, Shop
from the_app.models import AlternativeBrandName as ABN
from the_app.utils import strings, web

# human-readable info #########################################################

msg = {
    "-":
        "-" * settings.TERMINAL_WIDTH,
    "=":
        "=" * settings.TERMINAL_WIDTH,
    "help":
        "Collect all eurorack manufacturers sold at a specific shop.",
    "invalid_shop_name/slug":
        "[E] The argument '%s' is not recognized as any shop's name nor slug.",
    "got_shop_name/slug":
        "\n[*] Looking for a shop matching your input '%s'...",
    "got_shop":
        "[*] Found shop '%s' matching your input. Continuing..",
    "no_base_url":
        "[E] This shop has no valid 'base_url', so it's impossible visit.",
    "no_brands_path":
        "[E] This shop has no valid 'brands_path', so it's impossible to "
        "collect all brands sold at the shop.",
    "got_search_url":
        "[*] The URL that will be used for the search: '%s'",
    "shop_unreachable":
        "[E] Oops! There was an IOError while fetching data from "
        "this shop: '%s'.",
    "no_soup_call":
        "[E] Oops! No soup_call for searching all brands on '%s'.",
    "cannot_eval":
        "[E] Oh noes! There was an unexpected exception while trying to build "
        "the processing_function (eval: '%s') for retrieving brands:\n"
        "[*] '%s'",
    "cannot_process":
        "[E] Aiaiaiiii! The dynamically build processing_function crashed:\n"
        "[*] '%s'",
    "found_known_brand":
        "[+] This shop sells modules from '%s'. We'll add that information to "
        "the database..",
    "found_already_added_brand":
        "[*] This shop sells modules from '%s', but we already knew this.",
    "found_unknown_brand":
        "[!] We found an *apparently* unknown brand: '%s'..",
    "match_for_unknown_brand":
        "[!] However, the found name '%s' resembles the following brand(s)"
        "in our database:\n",
    "skip_invalid_name":
        "[!] Skipping found but invalid name '%s'.",
    "no_match_for_unknown_brand":
        "[-] Skipping: no partial matches, so brand '%s' will not be added "
        "to %s's list.",
    "add_partial_match?":
        "\n[?] Add partial match? n(o)/[1]/2/3/.../m >>> ",
    "sure_match?":
        "[?] Are you 100%% sure the shop sells brand '%s', although it "
        "actually lists '%s'? n/[y] >>> ",
    "linked_brands_ok":
        "[+] OK, we added '%s' to this shop's list.",
    "retarded_answer":
        "[E] Your input '%s' is retarded. Just look at the question!",
    "new_alt_brand_name":
        "[!] Added new AlternativeBrandName to database: %s",
    "abort":
        "[*] Aborting further execution.\n",
}


# exposed code ################################################################

class Command(BaseCommand):
    help = msg["help"]

    def add_arguments(self, parser):
        parser.add_argument("shop_slug", type=str)

    @staticmethod
    def initial_checks(shop):
        assert shop.base_url, msg["no_base_url"]
        assert shop.brands_path, msg["no_brands_path"]
        assert shop.search_brands_soup_call, msg["no_soup_call"] % shop.name

    @staticmethod
    def get_shop_instance(name_or_slug):
        p('got_shop_name/slug', name_or_slug)
        try:
            shop = Shop.objects.get(slug__startswith=name_or_slug)
        except Shop.DoesNotExist:
            try:
                shop = Shop.objects.get(name__startswith=name_or_slug)
            except Shop.DoesNotExist:
                p("invalid_shop_name/slug", name_or_slug)
                abort(-1)
        p("got_shop", shop.name)
        return shop

    def soup_to_brand_names(self, soup, soup_call):
        try:
            processing_function = eval(soup_call)
        except Exception as err:
            p('cannot_eval', soup_call, err)
            abort(-1)
        try:
            found_brand_names = []
            for found_name in processing_function(soup):
                found_name = found_name.strip()
                if found_name.lower() in settings.INVALID_BRAND_NAMES:
                    p("skip_invalid_name", found_name)
                    self.skipped_names.append(found_name)
                else:
                    found_brand_names.append(found_name)
        except Exception as err:
            p('cannot_process', err)
            abort(-1)
        sleep(1)
        return found_brand_names

    def skip_found_name(self, name, shop, must_sleep=False):
        """
        Skip a certain name at this shop.
        """
        p('no_match_for_unknown_brand', name, shop.name)
        self.skipped_names.append(name)
        if must_sleep:
            sleep(1)

    @staticmethod
    def get_matching_brands(slug):
        search_terms = slug.split(" ")
        matching_brands = []
        for search_term in search_terms:
            matching_brands += Brand.objects.filter(
                slug__icontains=search_term.strip())
        return matching_brands

    @staticmethod
    def list_partial_matches(name, matching_brands):
        p("match_for_unknown_brand", name)
        for i, matching_brand in enumerate(matching_brands):
            print("\t(%i) - %s" % (i + 1, matching_brand.name))

    def add(self, shop, found_name, brand):
        p('found_known_brand', found_name)
        shop.brands.add(brand)
        self.added_names.append(brand.name)

    def handle(self, *args, **options):

        start_time = time.time()
        shop = Command.get_shop_instance(options['shop_slug'])
        Command.initial_checks(shop)

        self.skipped_names = []
        self.added_names = []
        initial_brand_count = shop.brands.count()
        soup = web.get_full_soup(shop.brands_url())
        mined_brand_names = self.soup_to_brand_names(
            soup, shop.search_brands_soup_call)
        alt_brand_names = [abn.alternative_name.lower() for abn in
                           ABN.objects.all()]

        for mined_name in mined_brand_names:
            p("-")
            slug = strings.sluggify(mined_name)

            # If the lowercase mined name occurs in the list of alternative
            # brand names, we can add the recognized brand to this shop and
            # continue to the next mined name:

            if mined_name.lower() in alt_brand_names:
                abn = ABN.objects.filter(
                            alternative_name__icontains=mined_name.lower())[0]
                if shop.brands.filter(name=abn.brand.name).exists():
                    p("found_already_added_brand", abn.brand.name)
                else:
                    self.add(shop, mined_name, abn.brand)
                continue

            # We assume the mined name corresponds with a readily existing
            # database entry for a Brand: we try/except to get it, and add it
            # to the shop's list (if this weren't done before):

            try:
                known_brand = Brand.objects.get(slug=slug)
                if known_brand in shop.brands.all():
                    p('found_already_added_brand', known_brand.name)
                else:
                    self.add(shop, mined_name, known_brand)

            # When the mined name doesn't have a corresponding Brand in the
            # database, we look for all partial matches, list them, and the
            # user may or may not choose one of these partial matches:

            except Brand.DoesNotExist:
                p('found_unknown_brand', mined_name)
                matching_brands = Command.get_matching_brands(slug)
                if matching_brands:
                    Command.list_partial_matches(mined_name, matching_brands)
                    while True:
                        ans = q("add_partial_match?", default='1')
                        if ans == 'n':
                            self.skip_found_name(mined_name, shop)
                        else:
                            try:
                                ans_index = int(ans) - 1
                                existing_brand = matching_brands[ans_index]
                            except (ValueError, IndexError):
                                p("retarded_answer", ans)
                                continue
                            ans = q("sure_match?", existing_brand.name,
                                    mined_name, default='y')
                            if ans == 'y':
                                shop.brands.add(existing_brand)
                                p("linked_brands_ok", existing_brand.name)

                                if not ABN.objects.filter(
                                        alternative_name=mined_name).exists():
                                    abn = ABN.objects.create(
                                        alternative_name=mined_name,
                                        brand=existing_brand,
                                        shop=shop)
                                    p("new_alt_brand_name", abn)
                            else:
                                self.skip_found_name(mined_name, shop)
                        break
                else:
                    self.skip_found_name(mined_name, shop)

        final_brand_count = shop.brands.count()
        diff_brand_count = final_brand_count - initial_brand_count
        duration = time.time() - start_time

        nl()
        p('=')
        print('\nRESULT for indexing brands sold at shop "%s":\n' % shop.name)
        print("[*] command duration.............: %.2f sec" % duration)
        print("[*] shop's initial brand count...: %i" % initial_brand_count)
        print("[*] shop's final brand count.....: %i" % final_brand_count)

        print("[*] brands added to shop.........: %i" % diff_brand_count)
        if self.added_names:
            nl()
            for i, added_name in enumerate(self.added_names):
                print("\t%2.i - %s" % (i + 1, added_name))
            nl()

        self.skipped_names = filter(bool, self.skipped_names)
        print("[*] names found but skipped: %i" % len(self.skipped_names))
        if self.skipped_names:
            nl()
            for i, skipped_name in enumerate(self.skipped_names):
                print("\t%2.i - %s" % (i + 1, skipped_name))
            nl()

# local helper functions ######################################################


def nl():
    print("")


def p(key, *args):
    print(msg[key] % tuple(args))


def q(key, *args, **kwargs):
    default = kwargs.get('default', 'n')
    ans = raw_input(msg[key] % tuple(args))
    return ans[0].lower() if ans else default


def abort(statuscode=0):
    p('abort')
    sys.exit(statuscode)
