# Generated by Django 5.2 on 2025-06-03 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('a_posts', '0012_alter_comment_options_alter_reply_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
    ]
