# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 23, 17, 6, 6, 40791, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='shop',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 23, 17, 6, 6, 41562, tzinfo=utc)),
        ),
    ]
