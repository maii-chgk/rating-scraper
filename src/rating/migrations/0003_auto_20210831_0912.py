# Generated by Django 3.1 on 2021-08-31 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0002_auto_20210830_1021'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='newrating',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='newrating',
            name='player',
        ),
        migrations.RemoveField(
            model_name='newrating',
            name='result',
        ),
        migrations.AlterUniqueTogether(
            name='releaserating',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='releaserating',
            name='player',
        ),
        migrations.RemoveField(
            model_name='releaserating',
            name='release',
        ),
        migrations.AlterUniqueTogether(
            name='squad',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='squad',
            name='release',
        ),
        migrations.RemoveField(
            model_name='squad',
            name='team',
        ),
        migrations.RemoveField(
            model_name='squad',
            name='teamMembers',
        ),
        migrations.DeleteModel(
            name='Monogames',
        ),
        migrations.DeleteModel(
            name='Newrating',
        ),
        migrations.DeleteModel(
            name='Release',
        ),
        migrations.DeleteModel(
            name='Releaserating',
        ),
        migrations.DeleteModel(
            name='Squad',
        ),
    ]
