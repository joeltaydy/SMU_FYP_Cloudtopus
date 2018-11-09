# Generated by Django 2.0.7 on 2018-10-26 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Module_TeamManagement', '0009_auto_20181026_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='Telegram_Chats',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='Name', max_length=255)),
                ('type', models.CharField(choices=[('Channel', 'Channel'), ('Group', 'Group')], db_column='Type', max_length=10)),
                ('link', models.TextField(db_column='Link')),
                ('members', models.TextField(db_column='Members', null=True)),
            ],
            options={
                'db_table': 'Telegram_Chats',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='class',
            name='telegram_tools',
            field=models.ManyToManyField(db_column='Telegram_Chats', null=True, to='Module_TeamManagement.Telegram_Chats'),
        ),
    ]