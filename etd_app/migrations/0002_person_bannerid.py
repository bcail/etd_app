# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='bannerid',
            field=models.CharField(max_length=100, unique=True, null=True, blank=True),
        ),
    ]
