from django.contrib import admin
from django.db import models as db_models

from the_app.models import (
    Shop,
    Brand,
    AlternativeBrandName)


class ShopAdmin(admin.ModelAdmin):

    list_display = ('name', 'brand_count', 'country', 'created_at')
    search_fields = ('name',)

    fieldsets = [

        ('Shop info', {
            'fields': ['name', 'slug', 'country']}),

        ('URL info', {
            'fields':  ['base_url', 'brands_path', 'search_brands_soup_call'],
            'classes': ['collapse']}),

        ('Date info', {
            'fields':  ['created_at'],
            'classes': ['collapse']}),

        ('Brands sold', {
            'fields':  ['brands'],
            'classes': ['collapse']})
    ]


class AlternativeBrandNameInline(admin.TabularInline):
    model = AlternativeBrandName
    extra = 0
    fields = ('alternative_name', 'shop')
    ordering = ('shop',)


class AlternativeBrandNameAdmin(admin.ModelAdmin):
    list_display = ('alternative_name', 'brand', 'shop', 'created_at')
    search_fields = ('alternative_name',)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'created_via_modulargrid')
    search_fields = ('name',)
    inlines = [AlternativeBrandNameInline]

    fieldsets = [

        ('Brand information', {
            'fields':  ['name', 'slug', 'url', 'created_via_modulargrid']}),

        ('Date information',  {
            'fields':  ['created_at'],
            'classes': ['collapse']})
    ]


admin.site.register(Brand,
                    admin_class=BrandAdmin)

admin.site.register(Shop,
                    admin_class=ShopAdmin)

admin.site.register(AlternativeBrandName,
                    admin_class=AlternativeBrandNameAdmin)
