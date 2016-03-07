# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0012_candidate_embargo_end_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='GradschoolChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dissertation_fee', models.DateTimeField(null=True, blank=True)),
                ('bursar_receipt', models.DateTimeField(null=True, blank=True)),
                ('gradschool_exit_survey', models.DateTimeField(null=True, blank=True)),
                ('earned_docs_survey', models.DateTimeField(null=True, blank=True)),
                ('pages_submitted_to_gradschool', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='gradschool_checklist',
            field=models.ForeignKey(to='etd_app.GradschoolChecklist', null=True),
        ),
    ]