# Generated by Django 2.0.7 on 2018-10-04 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AWS_Credentials',
            fields=[
                ('account_number', models.CharField(db_column='Account_Number', max_length=255, primary_key=True, serialize=False)),
                ('access_key', models.TextField(db_column='Access_Key', null=True)),
                ('secret_access_key', models.TextField(db_column='Secret_Access_Key', null=True)),
            ],
            options={
                'db_table': 'AWS_Credentials',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Deployment_Package',
            fields=[
                ('deploymentid', models.CharField(db_column='Deployment_ID', max_length=255, primary_key=True, serialize=False)),
                ('gitlink', models.TextField(db_column='GitHub_Link')),
            ],
            options={
                'db_table': 'Deployment_Package',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Image_Details',
            fields=[
                ('imageId', models.CharField(db_column='Image_ID', max_length=255, primary_key=True, serialize=False)),
                ('imageName', models.CharField(db_column='Image_Name', max_length=255, null=True)),
                ('sharedAccNum', models.TextField(db_column='List_of_shared_account_number', null=True)),
            ],
            options={
                'db_table': 'Image_Details',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Server_Details',
            fields=[
                ('IP_address', models.CharField(db_column='IP_Address', max_length=255, primary_key=True, serialize=False)),
                ('instanceid', models.CharField(db_column='Instance_ID', max_length=255)),
                ('instanceName', models.CharField(db_column='Instance_Name', max_length=255, null=True)),
                ('state', models.CharField(db_column='Server_State', max_length=255, null=True)),
                ('account_number', models.ForeignKey(db_column='AWS_Account_Number', null=True, on_delete=django.db.models.deletion.CASCADE, to='Module_DeploymentMonitoring.AWS_Credentials')),
            ],
            options={
                'db_table': 'Server_Details',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='aws_credentials',
            name='imageDetails',
            field=models.ManyToManyField(db_column='Image_Details', null=True, to='Module_DeploymentMonitoring.Image_Details'),
        ),
    ]
