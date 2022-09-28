from django import forms
from .models import Buyer, IncommingShoe, InStorageShoe, Seller, SoldShoe

from django.core.validators import FileExtensionValidator


class DateInput(forms.DateInput):
    input_type = 'date'


class IncommingShoeForm(forms.ModelForm):
    class Meta:
        model = IncommingShoe
        fields = ['email', 'buy_price', 'name',
                  'size', 'order_date', 'seller', 'comment']
        labels = {
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'order_date': ('Data zamówienia'),
            'seller': ('Sprzedawca'),
            'comment': ('Uwagi'),
        }

        widgets = {
            'order_date': DateInput(),
        }


class EntryInForm(forms.ModelForm):
    class Meta:
        model = InStorageShoe
        fields = ['entry_date', 'buy_invoice_nr', 'buy_invoice_date']
        labels = {
            'entry_date': ('Data przyjęcia na magazyn'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'buy_invoice_date': ('Data faktury kupna'),
        }

        widgets = {
            'entry_date': DateInput(),
            'buy_invoice_date': DateInput(),
        }


class SendForm(forms.ModelForm):
    class Meta:
        model = SoldShoe
        fields = ['exit_date', 'sell_invoice_nr', 'sell_invoice_date',
                  'money_income_date', 'sell_price', 'buyer', 'tracking_nr', 'stockx_nr', 'cw']
        labels = {
            'exit_date': ('Data wydania z magazynu'),
            'sell_invoice_nr': ('Numer faktury sprzedaży'),
            'sell_invoice_date': ('Data faktury sprzedaży'),
            'money_income_date': ('Data wpływu na konto'),
            'sell_price': ('Cena sprzedaży [PLN]'),
            'buyer': ('Kupujący'),
            'tracking_nr': ('Numer listu przewozowego'),
            'stockx_nr': ('Numer StockX'),
            'cw': ('CW'),
        }

        widgets = {
            'exit_date': DateInput(),
            'sell_invoice_date': DateInput(),
            'money_income_date': DateInput(),
        }


class IncommingShoeForm(forms.ModelForm):
    class Meta:
        model = IncommingShoe
        fields = '__all__'

        labels = {
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'order_date': ('Data zamówienia'),
            'seller': ('Sprzedawca'),
            'comment': ('Uwagi'),
        }

        widgets = {
            'order_date': DateInput(format=('%Y-%m-%d')),
        }


class SoldMissingForm(forms.ModelForm):
    class Meta:
        model = SoldShoe
        exclude = ('storage_nr',)

        labels = {
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'order_date': ('Data zamówienia'),
            'seller': ('Sprzedawca'),
            'comment': ('Uwagi'),

            'entry_date': ('Data przyjęcia na magazyn'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'buy_invoice_date': ('Data faktury kupna'),

            'exit_date': ('Data wydania z magazynu'),
            'sell_invoice_nr': ('Numer faktury sprzedaży'),
            'sell_invoice_date': ('Data faktury sprzedaży'),
            'money_income_date': ('Data wpływu na konto'),
            'sell_price': ('Cena sprzedaży [PLN]'),
            'buyer': ('Kupujący'),
            'tracking_nr': ('Numer listu przewozowego'),
            'stockx_nr': ('Numer StockX'),
            'cw': ('CW'),
        }

        widgets = {
            'order_date': DateInput(format=('%Y-%m-%d')),

            'entry_date': DateInput(format=('%Y-%m-%d')),
            'buy_invoice_date': DateInput(format=('%Y-%m-%d')),

            'exit_date': DateInput(format=('%Y-%m-%d')),
            'sell_invoice_date': DateInput(format=('%Y-%m-%d')),
            'money_income_date': DateInput(format=('%Y-%m-%d')),
        }


class InStorageMissingForm(forms.ModelForm):
    class Meta:
        model = InStorageShoe
        fields = '__all__'

        labels = {
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'order_date': ('Data zamówienia'),
            'seller': ('Sprzedawca'),
            'comment': ('Uwagi'),

            'entry_date': ('Data przyjęcia na magazyn'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'buy_invoice_date': ('Data faktury kupna'),
        }

        widgets = {
            'order_date': DateInput(format=('%Y-%m-%d')),

            'entry_date': DateInput(format=('%Y-%m-%d')),
            'buy_invoice_date': DateInput(format=('%Y-%m-%d')),
        }


class InputCsvForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xls', 'xlsx'])])


class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = '__all__'

        labels = {
            'name': ('Nazwa'),
        }


class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = '__all__'

        labels = {
            'name': ('Nazwa'),
        }
