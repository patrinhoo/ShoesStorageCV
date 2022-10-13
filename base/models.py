from django.db import models


# Create your models here.
class Seller(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Buyer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class IncommingShoe(models.Model):
    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    order_date = models.DateField()
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name


class InStorageShoe(models.Model):
    storage_nr = models.IntegerField(unique=True, null=True)

    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    order_date = models.DateField()
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=200, blank=True)

    entry_date = models.DateField()
    buy_invoice_nr = models.CharField(max_length=30, blank=True)
    buy_invoice_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name


class SoldShoe(models.Model):
    storage_nr = models.IntegerField(unique=True, null=True)

    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    order_date = models.DateField()
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(max_length=200, blank=True)

    entry_date = models.DateField()
    buy_invoice_nr = models.CharField(max_length=30, blank=True)
    buy_invoice_date = models.DateField(blank=True, null=True)

    exit_date = models.DateField()
    sell_invoice_nr = models.CharField(max_length=30, blank=True)
    sell_invoice_date = models.DateField(blank=True, null=True)
    money_income_date = models.DateField(blank=True, null=True)
    sell_price = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True)
    buyer = models.ForeignKey(
        Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_nr = models.CharField(max_length=30, blank=True)
    stockx_nr = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return str(self.storage_nr) + '. ' + self.name

    class Meta:
        ordering = ('-exit_date', '-id')
