from django.db import migrations

def add_active_status(apps, schema_editor):
    ContractStatus = apps.get_model('your_app_name', 'ContractStatus')
    ContractStatus.objects.create(
        name="Active",
        description="Contract is currently in effect and being executed"
    )

class Migration(migrations.Migration):
    dependencies = [
        ('your_app_name', 'previous_migration'),
    ]

    operations = [
        migrations.RunPython(add_active_status),
    ]