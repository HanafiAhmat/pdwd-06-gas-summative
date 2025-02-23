# Generated by Django 5.1.1 on 2025-01-08 12:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_customergender_table'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_name', models.CharField(max_length=120)),
                ('recipient_phone', models.CharField(max_length=15)),
                ('postcode', models.CharField(max_length=10)),
                ('street', models.CharField(max_length=196)),
                ('street_optional', models.CharField(blank=True, default=None, max_length=196, null=True)),
                ('building_name', models.CharField(blank=True, default=None, max_length=196, null=True)),
                ('city', models.CharField(blank=True, default=None, max_length=196, null=True)),
                ('state', models.CharField(blank=True, default=None, max_length=196, null=True)),
                ('country', models.CharField(default='Singapore', max_length=196)),
                ('default', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'customer_addresses',
                'ordering': ['default'],
            },
        ),
    ]
