# Generated by Django 3.2 on 2021-09-03 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0004_alter_result_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='maiiAegis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournament',
            name='maiiAegisUpdatedAt',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='maiiRating',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournament',
            name='maiiRatingUpdatedAt',
            field=models.DateTimeField(null=True),
        ),
    ]