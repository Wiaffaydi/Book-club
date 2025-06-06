# Generated by Django 5.2 on 2025-04-16 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_bookview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='published_year',
        ),
        migrations.AddField(
            model_name='book',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='book',
            name='google_books_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='preview_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='thumbnail',
            field=models.URLField(),
        ),
    ]
