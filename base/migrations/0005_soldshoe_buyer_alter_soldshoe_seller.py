# Generated by Django 4.0.3 on 2022-08-05 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_instorageshoe_buy_invoice_nr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='soldshoe',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.buyer'),
        ),
        migrations.AlterField(
            model_name='soldshoe',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.seller'),
        ),
    ]
