# Generated by Django 2.0.5 on 2018-08-20 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0002_target'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='edu_course_time',
            field=models.FloatField(default=0, null=True),
        ),
    ]
