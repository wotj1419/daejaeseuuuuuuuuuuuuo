from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_user_profile_image'),
    ]

    operations = [
        migrations.CreateTable(
            name='TasteProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('embedding', models.JSONField(blank=True, default=list)),
                ('liked_movies_count', models.IntegerField(default=0)),
                ('top_genres', models.JSONField(blank=True, default=list)),
                ('summary', models.TextField(blank=True, default='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='taste_profile', to='accounts.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
