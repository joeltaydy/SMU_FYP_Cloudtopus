# Generated by Django 2.0.7 on 2018-11-08 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Module_TeamManagement', '0013_trailmix_information'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trailmix_information',
            name='course',
            field=models.ForeignKey(db_column='Course', null=True, on_delete=django.db.models.deletion.CASCADE, to='Module_TeamManagement.Course_Section'),
        ),
    ]
