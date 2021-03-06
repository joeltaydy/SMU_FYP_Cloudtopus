# Generated by Django 2.0.7 on 2018-10-25 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Module_DeploymentMonitoring', '0003_delete_deployment_package'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment_Package',
            fields=[
                ('deployment_id', models.AutoField(db_column='Deployment_ID', primary_key=True, serialize=False)),
                ('deployment_name', models.CharField(db_column='Deployment_Name', max_length=255, null=True)),
                ('deployment_link', models.TextField(db_column='Deployment_Link', null=True)),
            ],
            options={
                'db_table': 'Deployment_Package',
                'managed': True,
            },
        ),
    ]
