# Generated by Django 2.0.5 on 2018-07-27 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0015_auto_20180228_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approval_log',
            name='approverID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='approverID', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='approval_log',
            name='requesterID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requesterID', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='approvaldata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='blog_log',
            name='blogID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='blogdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='cafeteria_log',
            name='buyerID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='cafeteriadata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='ecm_log',
            name='userECMID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='ecmdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='education',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='emaildata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='emaileigvec',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='receiveID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='receiveID', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='emaillog',
            name='sendID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sendID', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='employeebiography',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='employeegrade',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='ep_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='epdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='flow',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='gatepass_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='gatepassdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='ims_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='imsdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='m_ep_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='m_epdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='meeting_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='meetingdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pc_control_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pc_control_log',
            name='requesterID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pc_out_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pc_out_log',
            name='requesterID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pcm_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='pcmdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='portable_out_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='portable_out_log',
            name='requesterID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='reward_log',
            name='rewardID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='score',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='snagraph',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='thanks_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='thanks_log',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='tms_log',
            name='employeeID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='executor', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='tms_log',
            name='employeeID2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cooperator', to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='tmsdata',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='vdi_indi_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='vdi_indi_log',
            name='user_indi_ID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='vdi_share_data',
            name='employeeID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
        migrations.AlterField(
            model_name='vdi_share_log',
            name='user_share_ID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='index.Employee'),
        ),
    ]
