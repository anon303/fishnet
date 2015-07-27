# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0004_auto_20150725_0739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shop',
            name='find_brands_soup_call',
        ),
        migrations.AddField(
            model_name='shop',
            name='search_brands_soup_call',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Soup call for finding all brands:', blank=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 25, 5, 44, 28, 632344, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='shop',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 25, 5, 44, 28, 633187, tzinfo=utc)),
        ),
    ]
