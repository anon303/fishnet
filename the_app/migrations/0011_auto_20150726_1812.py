# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0010_auto_20150726_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternativebrandname',
            name='brand',
            field=models.ForeignKey(related_name='alternative_names', to='the_app.Brand'),
        ),
        migrations.AlterField(
            model_name='alternativebrandname',
            name='shop',
            field=models.ForeignKey(related_name='alternative_brand_names', to='the_app.Shop', null=True),
        ),
    ]
