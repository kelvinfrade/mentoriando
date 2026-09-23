from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0009_email_verification'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='celular_encrypted',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='celular_hash',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True),
        ),
    ]