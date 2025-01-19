# Generated by Django 5.1.1 on 2025-01-08 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_customeraddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeraddress',
            name='recipient_name',
        ),
        migrations.AddField(
            model_name='customeraddress',
            name='recipient_first_name',
            field=models.CharField(default=' ', max_length=120),
        ),
        migrations.AddField(
            model_name='customeraddress',
            name='recipient_last_name',
            field=models.CharField(default=' ', max_length=120),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='postcode',
            field=models.CharField(default=' ', max_length=10),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='recipient_phone',
            field=models.CharField(default=' ', max_length=15),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='street',
            field=models.CharField(default=' ', max_length=196),
        ),
    ]
