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
    order_date = models.DateField()
    buy_invoice_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    buy_invoice_nr = models.CharField(max_length=30, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    comment = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return str(self.id) + '. ' + self.name


class InStorageShoe(models.Model):
    storage_nr = models.IntegerField(unique=True, null=True)
    entry_date = models.DateField()
    buy_invoice_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    buy_invoice_nr = models.CharField(max_length=30, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    comment = models.TextField(max_length=200, blank=True)

    def __str__(self):
        if self.storage_nr:
            return str(self.storage_nr) + '. ' + self.name + ' | ' + self.size + ' | ' + self.cw

        return '--. ' + self.name + ' | ' + self.size + ' | ' + self.cw


class SoldShoe(models.Model):
    storage_nr = models.IntegerField(unique=True, null=True)
    entry_date = models.DateField()
    exit_date = models.DateField()
    buy_invoice_date = models.DateField(blank=True, null=True)
    sell_invoice_date = models.DateField(blank=True, null=True)
    money_income_date = models.DateField(blank=True, null=True)
    stockx_invoice_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=200)
    size = models.CharField(max_length=20)
    cw = models.CharField(max_length=20, blank=True)
    stockx_nr = models.CharField(max_length=30, blank=True)
    sell_invoice_nr = models.CharField(max_length=30, blank=True)
    tracking_nr = models.CharField(max_length=30, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    buy_invoice_nr = models.CharField(max_length=30, blank=True)
    order_nr = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=200)
    buy_price = models.DecimalField(max_digits=7, decimal_places=2)
    sell_price = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True)
    eur_alias = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)
    buyer = models.ForeignKey(
        Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(max_length=200, blank=True)
    exchange_rate = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.storage_nr) + '. ' + self.name

    class Meta:
        ordering = ('-exit_date', '-id')


class OnAuctionShoe(models.Model):
    in_storage_shoe = models.OneToOneField(
        InStorageShoe, on_delete=models.CASCADE)
    alias_price = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)
    stockx_price = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)
    wtn_price = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.in_storage_shoe)

    class Meta:
        ordering = ('-in_storage_shoe__storage_nr',)
