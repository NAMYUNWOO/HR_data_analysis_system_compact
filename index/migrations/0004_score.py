# Generated by Django 2.0.5 on 2018-08-23 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0003_education_edu_course_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeID_confirm', models.IntegerField(default=0)),
                ('predict', models.FloatField(null=True)),
                ('intercept', models.FloatField(null=True)),
                ('grade_co_r3_avg', models.FloatField(null=True)),
                ('holiday', models.FloatField(null=True)),
                ('edu_course_cnt', models.FloatField(null=True)),
                ('edu_course_time', models.FloatField(null=True)),
                ('sendCnt_byLevelRatio', models.FloatField(null=True)),
                ('sendCnt_nwh_byLevelRatio', models.FloatField(null=True)),
                ('receiveCnt_byLevelRatio', models.FloatField(null=True)),
                ('nodeSize_byLevelRatio', models.FloatField(null=True)),
                ('nodeSize_byGroupRatio', models.FloatField(null=True)),
                ('token_receive_byLevelRatio', models.FloatField(null=True)),
                ('leadership_env_job', models.FloatField(null=True)),
                ('leadership_env', models.FloatField(null=True)),
                ('leadership_env_common', models.FloatField(null=True)),
                ('early_work', models.FloatField(null=True)),
                ('late_work', models.FloatField(null=True)),
                ('eval_date', models.DateTimeField()),
                ('start_date', models.DateTimeField()),
                ('employeeID', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee')),
            ],
        ),
    ]
