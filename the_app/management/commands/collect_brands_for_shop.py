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
from the_app.models import Brand, Shop, AlternativeBrandName
from the_app.utils import strings


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
        "\n[*] About to update the brands known to be sold at shop: '%s'",
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
        "[*] We found an *apparently* unknown brand: '%s'..",
    "match_for_unknown_brand":
        "[!] However, the found name '%s' resembles the following brand(s)"
        "in our database:\n",
    "skip_invalid_name":
        "[*] Skipping found but invalid name '%s'.",
    "no_match_for_unknown_brand":
        "[-] Skipping: brand '%s' will not be added to %s's list.",
    "add_partial_match?":
        "\n[?] Add partial match? n(o)/[1]/2/3/.../m >>> ",
    "sure_match?":
        "[?] Are you 100%% sure the shop sells brand '%s', although it "
        "actually lists '%s'? [n]/y >>> ",
    "linked_brands_ok":
        "[+] OK, we added '%s' to this shop's list.",
    "retarded_answer":
        "[E] Your input '%s' is retarded. Just look at the question, you $@#!",
    "abort":
        "[*] Aborting further execution.\n",
}


# exposed code ################################################################

class Command(BaseCommand):
    help = msg["help"]

    def add_arguments(self, parser):
        parser.add_argument("shop_slug", type=str)

    @staticmethod
    def get_shop_instance(name_or_slug):
        p('got_shop_name/slug', name_or_slug)
        try:
            return Shop.objects.get(slug=name_or_slug)
        except Shop.DoesNotExist:
            try:
                return Shop.objects.get(name=name_or_slug)
            except Shop.DoesNotExist:
                p("invalid_shop_name/slug", name_or_slug)
                abort(-1)

    @staticmethod
    def get_full_soup(search_url):
        try:
            full_html = urllib.urlopen(search_url)
        except IOError as err:
            p('shop_unreachable', err)
            abort(-1)
        else:
            full_soup = BeautifulSoup.BeautifulSoup(full_html)
            return full_soup

    def soup_to_brand_names(self, soup, soup_call):
        try:
            processing_function = eval(soup_call)
        except Exception as err:
            p('cannot_eval', soup_call, err)
            abort(-1)
        try:
            found_brand_names = []
            for found_name in processing_function(soup):
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

    def skip_found_name(self, name, shop, must_sleep=True):
        """
        Skip a certain name at this shop.
        """
        p('no_match_for_unknown_brand', name, shop.name)
        self.skipped_names.append(name)
        if must_sleep:
            sleep(1)

    def handle(self, *args, **options):
        start_time = time.time()
        shop = Command.get_shop_instance(options['shop_slug'])
        self.skipped_names = []
        initial_brand_count = shop.brands.count()

        assert shop.base_url, msg["no_base_url"]
        assert shop.brands_path, msg["no_brands_path"]
        assert shop.search_brands_soup_call, msg["no_soup_call"]

        search_url = urlparse.urljoin(shop.base_url, shop.brands_path)
        p('got_search_url', search_url)
        p('-')
        soup = Command.get_full_soup(search_url)
        mined_brand_names = self.soup_to_brand_names(
                                soup, shop.search_brands_soup_call)
        alt_brand_names = [obj.alternative_name for obj in
                           AlternativeBrandName.objects.filter(shop=shop)]
        for name in mined_brand_names:
            p("-")
            slug = strings.sluggify(name)
            if name in alt_brand_names:
                abn = AlternativeBrandName.objects.get(alternative_name=name)
                if Brand.objects.filter(name=abn.brand.name).exists():
                    p("found_already_added_brand", name)
                else:
                    p('found_known_brand', name)
                    shop.brands.add(abn.brand)
                sleep(1)
                continue
            try:
                known_brand = Brand.objects.get(slug=slug)
                if known_brand in shop.brands.all():
                    p('found_already_added_brand', name)
                    continue
                else:
                    p('found_known_brand', name)
                    shop.brands.add(known_brand)

            except Brand.MultipleObjectsReturned:
                set_trace()

            except Brand.DoesNotExist:
                p('found_unknown_brand', name)

                search_terms = slug.split(" ")
                matching_brands = []

                for search_term in search_terms:
                    matching_brands += Brand.objects.filter(
                        slug__icontains=search_term)

                if matching_brands:
                    p("match_for_unknown_brand", name)
                    for i, matching_brand in enumerate(matching_brands):
                        print("\t(%i) - %s" % (i + 1, matching_brand.name))
                    while True:
                        ans = raw_input(msg["add_partial_match?"])
                        ans = ans[0].lower() if ans else '1'
                        if ans == 'n':
                            self.skip_found_name(name, shop, False)
                        else:
                            try:
                                ans_index = int(ans) - 1
                                existing_brand = matching_brands[ans_index]
                            except (ValueError, IndexError):
                                p("retarded_answer", ans)
                                self.skip_found_name(name, shop, False)
                                continue
                            ans = q("sure_match?", existing_brand.name, name)
                            if ans == 'y':
                                shop.brands.add(existing_brand)
                                AlternativeBrandName.objects.create(
                                    alternative_name=name,
                                    brand=existing_brand,
                                    shop=shop)
                                p("linked_brands_ok", existing_brand.name)
                            else:
                                self.skip_found_name(name, shop, False)
                        sleep(1)
                        break
                else:
                    self.skip_found_name(name, shop)

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
        print("[*] names found but skipped......:\n")
        for i, skipped_name in enumerate(self.skipped_names):
            print("\t%2.i - %s" % (i + 1, skipped_name))
        nl()

# local helper functions ######################################################


def nl():
    print("")


def p(key, *args):
    print(msg[key] % tuple(args))


def q(key, *args, **kwargs):
    default_answer = 'n'
    ans = raw_input(msg[key] % tuple(args))
    return ans[0].lower() if ans else default_answer


def abort(statuscode=0):
    p('abort')
    sys.exit(statuscode)
