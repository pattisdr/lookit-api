# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-18 19:45
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


def set_study_types(apps, schema_editor):
    StudyType = apps.get_model('studies.StudyType')
    Study = apps.get_model('studies.Study')
    st, created = StudyType.objects.get_or_create(
        name='Ember Frame Player (default)',
        configuration={
            # task module should have a build_experiment method decorated as a
            # celery task that takes a study uuid and a preview kwarg which
            # defaults to true
            "task_module": "studies.tasks",
            "metadata": {
                # defines the default metadata fields for that type of study
                "fields": {
                    "addons_repo_url": settings.EMBER_ADDONS_REPO,
                    "last_known_player_sha": None,
                    "last_known_addons_sha": None
                }
            }
        }
    )
    ids = Study.objects.all().update(study_type=st)


def unset_study_types(apps, schema_editor):
    Study = apps.get_model('studies.Study')
    ids = Study.objects.all().update(study_type=None)


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0025_auto_20170818_1544'),
    ]

    operations = [
        migrations.RunPython(set_study_types, reverse_code=unset_study_types)
    ]
