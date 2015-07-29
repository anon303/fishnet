# 1) python imports: ##########################################################
import urlparse

# from ipdb import set_trace

# 2) django imports: ##########################################################
from django.db import models
from django.utils import timezone

from the_app.utils import strings


class ModelSuperClass(models.Model):
    """ Mixin for all of my models"""
    class Meta:
        abstract = True

    def was_saved(self):
        return self.pk is not None

    def field_names(self):
        return self._meta.get_all_field_names()

    def __unicode__(self):
        return 'pk=%s' % str(self.pk)


class Brand(ModelSuperClass):
    """
    Model representing an Eurorack manufacturer: e.g. Doepfer, Malekko etc.
    """
    name = models.CharField(max_length=64, null=False, blank=False)
    slug = models.CharField(max_length=64)
    url = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_via_modulargrid = models.BooleanField(null=False, default=False)

    def __unicode__(self):
        return self.slug


class Shop(ModelSuperClass):
    """
    Model representing webshops where you can buy modules: e.g Schneidersladen,
    Postmodular or Analog Haven.
    """
    brands = models.ManyToManyField(Brand, null=True, blank=True)
    name = models.CharField(max_length=64, null=False, blank=False)
    slug = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    country = models.CharField(max_length=64, null=True, blank=True)
    base_url = models.CharField(max_length=256)
    brands_path = models.CharField(
        'Path to mine brands',
        max_length=256,
        null=True,
        blank=True)
    search_brands_soup_call = models.CharField(
        'Soup call to mine brands',
        max_length=256,
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        self.slug = strings.sluggify(self.name)
        super(Shop, self).save(*args, **kwargs)

    def brands_url(self):
        """
        Get the full URL for searching the shop's brands.
        """
        return urlparse.urljoin(self.base_url, self.brands_path)

    def brand_count(self):
        """
        Function that returns False iff the shop has 0 brands, and True
        otherwise.
        """
        return self.brands.count()

    brand_count.short_description = 'Amt. of brands'

    def __unicode__(self):
        return self.slug


class AlternativeBrandName(ModelSuperClass):
    """
    Model representing an alternative name for a brand. The brand is always
    related via a FK, and a shop might be related via a FK.
    """
    alternative_name = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    brand = models.ForeignKey(Brand, related_name='alternative_names')
    shop = models.ForeignKey(Shop, related_name='alternative_brand_names',
                             null=True, blank=True)

    def __unicode__(self):
        return "db-name='%s' vs. alternative='%s'" \
               % (self.brand.name, self.alternative_name)
