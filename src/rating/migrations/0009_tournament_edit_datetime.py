# Generated by Django 3.2 on 2021-11-02 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0008_auto_20211027_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='edit_datetime',
            field=models.DateTimeField(null=True),
        ),
    ]
