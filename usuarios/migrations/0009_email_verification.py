from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0008_userprofile_session_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_verification_token_hash',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]