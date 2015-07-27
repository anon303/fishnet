# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0013_auto_20150726_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='url',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
