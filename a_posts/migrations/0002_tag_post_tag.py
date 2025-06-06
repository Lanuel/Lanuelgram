# Generated by Django 5.2 on 2025-04-18 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('slug', models.CharField(max_length=20)),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(to='a_posts.tag'),
        ),
    ]
