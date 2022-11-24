from django import forms
from .models import Buyer, IncommingShoe, InStorageShoe, Seller, SoldShoe, OnAuctionShoe

from django.core.validators import FileExtensionValidator


class DateInput(forms.DateInput):
    input_type = 'date'


class EntryInForm(forms.ModelForm):
    class Meta:
        model = InStorageShoe
        fields = ['storage_nr', 'entry_date']
        labels = {
            'storage_nr': ('Numer magazynowy'),
            'entry_date': ('Data przyjęcia na magazyn'),
        }

        widgets = {
            'entry_date': DateInput(),
        }


class SendForm(forms.ModelForm):
    class Meta:
        model = SoldShoe
        fields = ['exit_date', 'sell_invoice_date', 'money_income_date',
                  'stockx_invoice_date', 'stockx_nr', 'sell_invoice_nr',
                  'tracking_nr', 'sell_price', 'eur_alias', 'buyer', 'exchange_rate']
        labels = {
            'exit_date': ('Data wydania z magazynu'),
            'sell_invoice_date': ('Data faktury sprzedaży'),
            'money_income_date': ('Data wpływu na konto'),
            'stockx_invoice_date': ('Data faktury StockX'),
            'stockx_nr': ('Numer StockX'),
            'sell_invoice_nr': ('Numer faktury sprzedaży'),
            'tracking_nr': ('Numer listu przewozowego'),
            'sell_price': ('Cena sprzedaży [PLN]'),
            'eur_alias': ('Cena Alias [EUR]'),
            'buyer': ('Kupujący'),
            'exchange_rate': ('Kurs waluty'),
        }

        widgets = {
            'exit_date': DateInput(),
            'sell_invoice_date': DateInput(),
            'money_income_date': DateInput(),
            'stockx_invoice_date': DateInput(),
        }


class IncommingShoeForm(forms.ModelForm):
    class Meta:
        model = IncommingShoe
        fields = '__all__'

        labels = {
            'order_date': ('Data zamówienia'),
            'buy_invoice_date': ('Data faktury kupna'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'cw': ('CW'),
            'seller': ('Sprzedawca'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'order_nr': ('Numer zamówienia'),
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'comment': ('Uwagi'),
        }

        widgets = {
            'order_date': DateInput(format=('%Y-%m-%d')),
            'buy_invoice_date': DateInput(),
        }


class SoldMissingForm(forms.ModelForm):
    class Meta:
        model = SoldShoe
        exclude = ('storage_nr',)

        labels = {
            'entry_date': ('Data przyjęcia na magazyn'),
            'exit_date': ('Data wydania z magazynu'),
            'buy_invoice_date': ('Data faktury kupna'),
            'sell_invoice_date': ('Data faktury sprzedaży'),
            'money_income_date': ('Data wpływu na konto'),
            'stockx_invoice_date': ('Data faktury StockX'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'cw': ('CW'),
            'stockx_nr': ('Numer StockX'),
            'sell_invoice_nr': ('Numer faktury sprzedaży'),
            'tracking_nr': ('Numer listu przewozowego'),
            'seller': ('Sprzedawca'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'order_nr': ('Numer zamówienia'),
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'sell_price': ('Cena sprzedaży [PLN]'),
            'eur_alias': ('Cena Alias [EUR]'),
            'buyer': ('Kupujący'),
            'comment': ('Uwagi'),
            'exchange_rate': ('Kurs waluty'),

        }

        widgets = {
            'entry_date': DateInput(format=('%Y-%m-%d')),
            'exit_date': DateInput(format=('%Y-%m-%d')),
            'buy_invoice_date': DateInput(format=('%Y-%m-%d')),
            'sell_invoice_date': DateInput(format=('%Y-%m-%d')),
            'money_income_date': DateInput(format=('%Y-%m-%d')),
            'stockx_invoice_date': DateInput(format=('%Y-%m-%d')),
        }


class InStorageMissingForm(forms.ModelForm):
    class Meta:
        model = InStorageShoe
        exclude = ('storage_nr',)

        labels = {
            'entry_date': ('Data przyjęcia na magazyn'),
            'buy_invoice_date': ('Data faktury kupna'),
            'name': ('Nazwa buta'),
            'size': ('Rozmiar'),
            'cw': ('CW'),
            'seller': ('Sprzedawca'),
            'buy_invoice_nr': ('Numer faktury kupna'),
            'order_nr': ('Numer zamówienia'),
            'email': ('Email'),
            'buy_price': ('Cena zakupu [PLN]'),
            'comment': ('Uwagi'),
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


class OnAuctionForm(forms.ModelForm):
    class Meta:
        model = OnAuctionShoe

        fields = '__all__'

    def is_valid(self):
        valid = super(OnAuctionForm, self).is_valid()

        any_price = True if self.cleaned_data['alias_price'] or self.cleaned_data[
            'stockx_price'] or self.cleaned_data['wtn_price'] else False

        if valid and any_price:
            return True
        else:
            return False
