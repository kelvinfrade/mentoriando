from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpf_encrypted', models.TextField()),
                ('cpf_hash', models.CharField(db_index=True, max_length=64, unique=True)),
                ('totp_secret', models.CharField(blank=True, max_length=64)),
                ('mfa_enabled', models.BooleanField(default=False)),
                ('trusted_device_hash', models.CharField(blank=True, max_length=64)),
                ('session_version', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
    ]