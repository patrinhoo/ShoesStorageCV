# Generated by Django 4.0.3 on 2022-08-30 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_soldshoe_buyer_alter_soldshoe_seller'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='soldshoe',
            options={'ordering': ('-exit_date', '-id')},
        ),
    ]
