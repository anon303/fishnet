# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0014_auto_20150726_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternativebrandname',
            name='shop',
            field=models.ForeignKey(related_name='alternative_brand_names', blank=True, to='the_app.Shop', null=True),
        ),
    ]
