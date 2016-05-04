# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import simapp.storage
import django.utils.timezone
import simapp.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_id', models.CharField(unique=True, max_length=200)),
                ('model_format', models.IntegerField(default=1)),
                ('file', models.FileField(storage=simapp.storage.OverwriteStorage(), max_length=200, upload_to=b'model')),
                ('md5', models.CharField(max_length=36)),
            ],
            options={
                'verbose_name': 'CompModel',
                'verbose_name_plural': 'CompModels',
            },
        ),
        migrations.CreateModel(
            name='Core',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=200)),
                ('cpu', models.IntegerField()),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Core',
                'verbose_name_plural': 'Cores',
            },
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('method_type', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Method',
                'verbose_name_plural': 'Methods',
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('unit', models.CharField(max_length=50)),
                ('parameter_type', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_type', models.IntegerField(default=1)),
                ('file', models.FileField(storage=simapp.storage.OverwriteStorage(), max_length=200, upload_to=simapp.models.result_filename)),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.IntegerField(default=1)),
                ('value', models.CharField(max_length=40)),
                ('datatype', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Simulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1)),
                ('time_create', models.DateTimeField(default=django.utils.timezone.now)),
                ('time_assign', models.DateTimeField(null=True, blank=True)),
                ('time_sim', models.DateTimeField(null=True, blank=True)),
                ('core', models.ForeignKey(blank=True, to='simapp.Core', null=True)),
                ('parameters', models.ManyToManyField(to='simapp.Parameter')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.IntegerField(default=0)),
                ('info', models.TextField(null=True, blank=True)),
                ('status', models.IntegerField(default=1)),
                ('method', models.ForeignKey(related_name='tasks', to='simapp.Method')),
                ('model', models.ForeignKey(related_name='tasks', to='simapp.CompModel')),
            ],
        ),
        migrations.AddField(
            model_name='simulation',
            name='task',
            field=models.ForeignKey(related_name='simulations', to='simapp.Task'),
        ),
        migrations.AddField(
            model_name='result',
            name='simulation',
            field=models.ForeignKey(related_name='results', to='simapp.Simulation'),
        ),
        migrations.AlterUniqueTogether(
            name='parameter',
            unique_together=set([('key', 'value')]),
        ),
        migrations.AddField(
            model_name='method',
            name='settings',
            field=models.ManyToManyField(to='simapp.Setting'),
        ),
        migrations.AlterUniqueTogether(
            name='core',
            unique_together=set([('ip', 'cpu')]),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together=set([('model', 'method', 'info')]),
        ),
    ]
