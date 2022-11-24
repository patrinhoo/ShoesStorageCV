# Generated by Django 4.1.3 on 2022-11-24 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0007_incommingshoe_cw_incommingshoe_order_nr_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="instorageshoe",
            name="order_date",
        ),
        migrations.RemoveField(
            model_name="soldshoe",
            name="order_date",
        ),
        migrations.AddField(
            model_name="incommingshoe",
            name="buy_invoice_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="incommingshoe",
            name="buy_invoice_nr",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="soldshoe",
            name="eur_alias",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=7, null=True
            ),
        ),
        migrations.AddField(
            model_name="soldshoe",
            name="exchange_rate",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=5, null=True
            ),
        ),
        migrations.AddField(
            model_name="soldshoe",
            name="stockx_invoice_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="OnAuctionShoe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "alias_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=7, null=True
                    ),
                ),
                (
                    "stockx_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=7, null=True
                    ),
                ),
                (
                    "wtn_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=7, null=True
                    ),
                ),
                (
                    "in_storage_shoe",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.instorageshoe",
                    ),
                ),
            ],
            options={
                "ordering": ("-in_storage_shoe__storage_nr",),
            },
        ),
    ]