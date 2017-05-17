# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-24 17:31
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import localflavor.us.models
import project.fields.datetime_aware_jsonfield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.EmailField(max_length=254, unique=True)),
                ('given_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(blank=True, max_length=255)),
                ('family_name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DemographicData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('number_of_children', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('>10', 'More than 10')], max_length=3)),
                ('child_birthdays', django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), size=None, verbose_name="children's birthdays")),
                ('languages_spoken_at_home', models.TextField(verbose_name='languages spoken at home')),
                ('number_of_guardians', models.CharField(choices=[('1', '1'), ('2', '2'), ('3>', '3 or more'), ('varies', 'varies')], max_length=6)),
                ('number_of_guardians_explanation', models.TextField()),
                ('race_identification', models.CharField(choices=[('white', 'White'), ('hisp', 'Hispanic, Latino, or Spanish origin'), ('black', 'Black or African American'), ('asian', 'Asian'), ('native', 'American Indian or Alaska Native'), ('mideast-naf', 'Middle Eastern or North African'), ('hawaiian-pac-isl', 'Native Hawaiian or Other Pacific Islander'), ('other', 'Another race, ethnicity, or origin')], max_length=16)),
                ('age', models.CharField(choices=[('<18', 'under 18'), ('18-21', '18-21'), ('22-24', '22-24'), ('25-29', '25-29'), ('30-34', '30-34'), ('35-39', '35-39'), ('40-44', '40-44'), ('45-59', '45-49'), ('50s', '50-59'), ('60s', '60-69'), ('>70', '70 or over')], max_length=5)),
                ('gender', models.CharField(choices=[('m', 'male'), ('f', 'female'), ('o', 'other'), ('na', 'prefer not to answer')], max_length=2)),
                ('education_level', models.CharField(choices=[('some', 'some or attending high school'), ('hs', 'high school diploma or GED'), ('col', 'some or attending college'), ('assoc', '2-year college degree'), ('bach', '4-year college degree'), ('grad', 'some or attending graduate or professional school'), ('prof', 'graduate or professional degree')], max_length=5)),
                ('spouse_education_level', models.CharField(choices=[('some', 'some or attending high school'), ('hs', 'high school diploma or GED'), ('col', 'some or attending college'), ('assoc', '2-year college degree'), ('bach', '4-year college degree'), ('grad', 'some or attending graduate or professional school'), ('prof', 'graduate or professional degree'), ('na', 'not applicable - no spouse or partner')], max_length=5)),
                ('annual_income', models.CharField(choices=[('0', '0'), ('5000', '5000'), ('10000', '10000'), ('15000', '15000'), ('20000', '20000'), ('30000', '30000'), ('40000', '40000'), ('50000', '50000'), ('60000', '60000'), ('70000', '70000'), ('80000', '80000'), ('90000', '90000'), ('100000', '100000'), ('110000', '110000'), ('120000', '120000'), ('130000', '130000'), ('140000', '140000'), ('150000', '150000'), ('160000', '160000'), ('170000', '170000'), ('180000', '180000'), ('190000', '190000'), ('>200000', 'over 200000'), ('na', 'prefer not to answer')], max_length=7)),
                ('number_of_books', models.IntegerField()),
                ('additional_comments', models.TextField()),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('state', localflavor.us.models.USStateField(max_length=2)),
                ('density', models.CharField(choices=[('urban', 'urban'), ('suburban', 'suburban'), ('rural', 'rural')], max_length=8)),
                ('extra', project.fields.datetime_aware_jsonfield.DateTimeAwareJSONField()),
                ('previous', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_demographic_data', related_query_name='next_demographic_data', to='accounts.DemographicData')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demographics', related_query_name='demographics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField(verbose_name='Website')),
            ],
            options={
                'permissions': (('is_admin', 'Organization Administrator'), ('can_add_researchers', 'Can Add Researchers'), ('can_approve_studies', 'Can Approve Studies'), ('can_disable_studies', 'Can Disable Studies')),
            },
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', related_query_name='user', to='accounts.Organization'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
