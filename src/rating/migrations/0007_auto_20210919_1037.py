# Generated by Django 3.2 on 2021-09-19 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0006_basesquad_season'),
    ]

    operations = [
        migrations.RenameField(
            model_name='basesquad',
            old_name='end',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='basesquad',
            old_name='start',
            new_name='start_date',
        ),
        migrations.RenameField(
            model_name='tournament',
            old_name='maiiRating',
            new_name='maii_rating',
        ),
    ]