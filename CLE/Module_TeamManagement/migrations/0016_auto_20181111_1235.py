# Generated by Django 2.0.7 on 2018-11-11 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Module_TeamManagement', '0015_auto_20181109_0051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cloud_learning_tools',
            name='course_section',
        ),
        migrations.AddField(
            model_name='cloud_learning_tools',
            name='course_section',
            field=models.ManyToManyField(to='Module_TeamManagement.Course_Section'),
        ),
    ]