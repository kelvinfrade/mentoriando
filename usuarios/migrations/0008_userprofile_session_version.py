from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0007_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='session_version',
            field=models.PositiveIntegerField(default=1),
        ),
    ]