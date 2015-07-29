# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0015_auto_20150726_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='brands',
            field=models.ManyToManyField(to='the_app.Brand', null=True, blank=True),
        ),
    ]
