# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('the_app', '0008_auto_20150726_0755'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternativeBrandName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alternative_name', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='brand',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 26, 7, 51, 53, 26251, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='shop',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 26, 7, 51, 53, 27168, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='alternativebrandname',
            name='brand',
            field=models.ForeignKey(to='the_app.Brand'),
        ),
        migrations.AddField(
            model_name='alternativebrandname',
            name='shop',
            field=models.ForeignKey(to='the_app.Shop', null=True),
        ),
    ]
