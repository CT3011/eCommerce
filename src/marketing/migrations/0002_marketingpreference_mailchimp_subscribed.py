# Generated by Django 4.2.1 on 2023-06-09 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketingpreference',
            name='mailchimp_subscribed',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]