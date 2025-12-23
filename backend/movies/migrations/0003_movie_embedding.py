from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_movie_catchphrase'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='embedding',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='movie',
            name='embedding_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
