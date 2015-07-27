# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0002_auto_20150723_1906'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shop',
            old_name='url',
            new_name='base_url',
        ),
        migrations.AddField(
            model_name='shop',
            name='brands_path',
            field=models.CharField(max_length=256, null=True, verbose_name=b'URL path for finding all brands sold at this shop.', blank=True),
        ),
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 25, 3, 47, 16, 896352, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='shop',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 25, 3, 47, 16, 897169, tzinfo=utc)),
        ),
    ]
