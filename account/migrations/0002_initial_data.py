from django.db import migrations

def initial_genders(apps, schema_editor):
    CustomerGender = apps.get_model("account", "CustomerGender")
    CustomerGender.objects.bulk_create(
        [
            CustomerGender(name="Undisclosed", code="u", default=True),
            CustomerGender(name="Female", code="f"),
            CustomerGender(name="Male", code="m"),
        ]
    )

class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_genders),
    ]
