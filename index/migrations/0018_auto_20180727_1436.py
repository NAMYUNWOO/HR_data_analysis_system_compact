# Generated by Django 2.0.5 on 2018-07-27 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0017_auto_20180727_1344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='edu_credit_in',
        ),
        migrations.RemoveField(
            model_name='education',
            name='edu_credit_out',
        ),
        migrations.RemoveField(
            model_name='education',
            name='edu_nbr',
        ),
        migrations.RemoveField(
            model_name='education',
            name='lang_nbr',
        ),
        migrations.RemoveField(
            model_name='education',
            name='opic',
        ),
        migrations.RemoveField(
            model_name='education',
            name='sjpt',
        ),
        migrations.RemoveField(
            model_name='education',
            name='toeic',
        ),
        migrations.RemoveField(
            model_name='education',
            name='tsc',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='age',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='coreyn',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='istarget',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='pmlevel',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='sex',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='work_duration',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='age',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='coreyn',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='eval_date',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='istarget',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='pmlevel',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='sex',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='employeebiography',
            name='work_duration',
        ),
    ]