from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_friends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='friends',
        ),
        migrations.AddField(
            model_name='user',
            name='followings',
            field=models.ManyToManyField(
                blank=True,
                related_name='followers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
