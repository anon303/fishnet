# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0011_auto_20150726_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='created_via_modulargrid',
            field=models.BooleanField(default=False),
        ),
    ]
