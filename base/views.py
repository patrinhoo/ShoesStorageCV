import codecs
import csv
from datetime import datetime
from itertools import chain
from operator import attrgetter

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Max, Q
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView

from .forms import (BuyerForm, EntryInForm, IncommingShoeForm, InputCsvForm,
                    InStorageMissingForm, OnAuctionForm, SellerForm, SendForm,
                    SoldMissingForm)
from .models import (Buyer, IncommingShoe, InStorageShoe, OnAuctionShoe,
                     Seller, SoldShoe)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# Function based views
@login_required(login_url='/login/')
def incomming_csv(request):
    incomming_shoes = IncommingShoe.objects.all()

    name = request.GET.get('n')
    if name:
        incomming_shoes = incomming_shoes.filter(name__contains=name)

    seller = request.GET.get('s')
    if seller:
        incomming_shoes = incomming_shoes.filter(seller__name__contains=seller)

    order_nr = request.GET.get('on')
    if order_nr:
        incomming_shoes = incomming_shoes.filter(order_nr__contains=order_nr)

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        incomming_shoes = incomming_shoes.filter(order_date=order_date)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')

    response = StreamingHttpResponse((chain([codecs.BOM_UTF8],
                                            writer.writerow(['Nr', 'Data zamowienia', 'Data faktury kupna', 'Nazwa produktu', 'Rozmiar', 'CW',
                                                             'Sprzedawca', 'Numer faktury kupna', 'Nr zamowienia', 'Email', 'Cena kupna', 'Komentarz']),
                                            (writer.writerow([nr+1, shoe.order_date, shoe.buy_invoice_date, shoe.name, shoe.size, shoe.cw, shoe.seller,
                                                              shoe.buy_invoice_nr, shoe.order_nr, shoe.email, shoe.buy_price, shoe.comment])
                                             for nr, shoe in enumerate(incomming_shoes.iterator(chunk_size=25))))),
                                     content_type='text/csv',)

    response['Content-Disposition'] = f'attachment; filename="PRZYCHODZACE_{datetime.now()}.csv"'

    return response


@login_required(login_url='/login/')
def storage_csv(request):
    in_storage_shoes = InStorageShoe.objects.all()

    name = request.GET.get('n')
    if name:
        in_storage_shoes = in_storage_shoes.filter(name__contains=name)

    seller = request.GET.get('s')
    if seller:
        in_storage_shoes = in_storage_shoes.filter(
            seller__name__contains=seller)

    order_nr = request.GET.get('on')
    if order_nr:
        in_storage_shoes = in_storage_shoes.filter(
            order_nr__contains=order_nr)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        in_storage_shoes = in_storage_shoes.filter(entry_date=entry_date)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')

    response = StreamingHttpResponse((chain([codecs.BOM_UTF8],
                                            writer.writerow(['Nr magazynowy', 'Data przyjecia', 'Data faktury kupna', 'Nazwa produktu',
                                                             'Rozmiar',  'CW', 'Sprzedawca', 'Nr faktury kupna', 'Nr zamowienia',
                                                             'Email', 'Cena kupna', 'Komentarz']),
                                            (writer.writerow([shoe.storage_nr, shoe.entry_date, shoe.buy_invoice_date, shoe.name,
                                                              shoe.size, shoe.cw, shoe.seller, shoe.buy_invoice_nr, shoe.order_nr,
                                                              shoe.email, shoe.buy_price, shoe.comment]) for shoe in in_storage_shoes.iterator(chunk_size=25)))),
                                     content_type='text/csv',)

    response['Content-Disposition'] = f'attachment; filename="MAGAZYN_{datetime.now()}.csv"'

    return response


@ login_required(login_url='/login/')
def archives_csv(request):
    sold_shoes = SoldShoe.objects.all()

    name = request.GET.get('n')
    if name:
        sold_shoes = sold_shoes.filter(name__contains=name)

    seller = request.GET.get('s')
    if seller:
        sold_shoes = sold_shoes.filter(seller__name__contains=seller)

    buyer = request.GET.get('b')
    if buyer:
        sold_shoes = sold_shoes.filter(buyer__name__contains=buyer)

    order_nr = request.GET.get('on')
    if order_nr:
        sold_shoes = sold_shoes.filter(order_nr__contains=order_nr)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        sold_shoes = sold_shoes.filter(entry_date=entry_date)

    send_date = request.GET.get('sd')
    if send_date:
        send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
        sold_shoes = sold_shoes.filter(exit_date=send_date)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')

    response = StreamingHttpResponse((chain([codecs.BOM_UTF8],
                                            writer.writerow(['Nr magazynowy', 'Data przyjecia', 'Data wydania', 'Data faktury kupna',
                                                             'Data faktury sprzedazy', 'Data wpływu na konto', 'Data faktury StockX',
                                                             'Nazwa produktu', 'Rozmiar', 'CW', 'Nr StockX', 'Nr faktury sprzedazy',
                                                             'Numer listu przewozowego', 'Sprzedawca', 'Nr faktury kupna', 'Nr zamowienia',
                                                             'Email', 'Cena kupna', 'Cena sprzedazy', 'Cena Alias', 'Kupujący',
                                                             'Komentarz', 'Kurs waluty']),
                                            (writer.writerow([shoe.storage_nr, shoe.entry_date, shoe.exit_date, shoe.buy_invoice_date,
                                                              shoe.sell_invoice_date, shoe.money_income_date, shoe.stockx_invoice_date,
                                                              shoe.name, shoe.size, shoe.cw, shoe.stockx_nr, shoe.sell_invoice_nr,
                                                              shoe.tracking_nr, shoe.seller, shoe.buy_invoice_nr, shoe.order_nr,
                                                              shoe.email, shoe.buy_price, shoe.sell_price, shoe.eur_alias, shoe.buyer,
                                                              shoe.comment, shoe.exchange_rate]) for shoe in sold_shoes.iterator(chunk_size=25)))),
                                     content_type='text/csv',)

    response['Content-Disposition'] = f'attachment; filename="ARCHIWUM_{datetime.now()}.csv"'

    return response


@ login_required(login_url='/login/')
def missing_storage_csv(request):
    missing_storage = InStorageShoe.objects.filter(
        Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True))

    name = request.GET.get('n')
    if name:
        missing_storage = missing_storage.filter(
            name__contains=name)

    seller = request.GET.get('s')
    if seller:
        missing_storage = missing_storage.filter(
            seller__name__contains=seller)

    order_nr = request.GET.get('on')
    if order_nr:
        missing_storage = missing_storage.filter(
            order_nr__contains=order_nr)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        missing_storage = missing_storage.filter(entry_date=entry_date)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')

    response = StreamingHttpResponse((chain([codecs.BOM_UTF8],
                                            writer.writerow(['Nr magazynowy', 'Data przyjecia', 'Data faktury kupna', 'Nazwa produktu',
                                                             'Rozmiar',  'CW', 'Sprzedawca', 'Nr faktury kupna', 'Nr zamowienia',
                                                             'Email', 'Cena kupna', 'Komentarz']),
                                            (writer.writerow([shoe.storage_nr, shoe.entry_date, shoe.buy_invoice_date, shoe.name,
                                                              shoe.size, shoe.cw, shoe.seller, shoe.buy_invoice_nr, shoe.order_nr,
                                                              shoe.email, shoe.buy_price, shoe.comment]) for shoe in missing_storage.iterator(chunk_size=25)))),
                                     content_type='text/csv',)

    response['Content-Disposition'] = f'attachment; filename="NO_DATA_MAGAZYN_{datetime.now()}.csv"'

    return response


@ login_required(login_url='/login/')
def missing_archives_csv(request):
    missing_archives = SoldShoe.objects.filter(
        Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True) |
        Q(sell_invoice_nr__exact='') | Q(sell_invoice_date__isnull=True) |
        Q(money_income_date__isnull=True) | Q(sell_price__isnull=True) |
        Q(buyer__isnull=True) | Q(tracking_nr__exact='') |
        Q(stockx_nr__exact='') | Q(cw__exact=''))

    name = request.GET.get('n')
    if name:
        missing_archives = missing_archives.filter(
            name__contains=name)

    seller = request.GET.get('s')
    if seller:
        missing_archives = missing_archives.filter(
            seller__name__contains=seller)

    buyer = request.GET.get('b')
    if buyer:
        missing_archives = missing_archives.filter(
            buyer__name__contains=buyer)

    order_nr = request.GET.get('on')
    if order_nr:
        missing_archives = missing_archives.filter(
            order_nr__contains=order_nr)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        missing_archives = missing_archives.filter(entry_date=entry_date)

    send_date = request.GET.get('sd')
    if send_date:
        send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
        missing_archives = missing_archives.filter(exit_date=send_date)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')

    response = StreamingHttpResponse((chain([codecs.BOM_UTF8],
                                            writer.writerow(['Nr magazynowy', 'Data przyjecia', 'Data wydania', 'Data faktury kupna',
                                                             'Data faktury sprzedazy', 'Data wpływu na konto', 'Data faktury StockX',
                                                             'Nazwa produktu', 'Rozmiar', 'CW', 'Nr StockX', 'Nr faktury sprzedazy',
                                                             'Numer listu przewozowego', 'Sprzedawca', 'Nr faktury kupna', 'Nr zamowienia',
                                                             'Email', 'Cena kupna', 'Cena sprzedazy', 'Cena Alias', 'Kupujący',
                                                             'Komentarz', 'Kurs waluty']),
                                            (writer.writerow([shoe.storage_nr, shoe.entry_date, shoe.exit_date, shoe.buy_invoice_date,
                                                              shoe.sell_invoice_date, shoe.money_income_date, shoe.stockx_invoice_date,
                                                              shoe.name, shoe.size, shoe.cw, shoe.stockx_nr, shoe.sell_invoice_nr,
                                                              shoe.tracking_nr, shoe.seller, shoe.buy_invoice_nr, shoe.order_nr,
                                                              shoe.email, shoe.buy_price, shoe.sell_price, shoe.eur_alias, shoe.buyer,
                                                              shoe.comment, shoe.exchange_rate]) for shoe in missing_archives.iterator(chunk_size=25)))),
                                     content_type='text/csv',)

    response['Content-Disposition'] = f'attachment; filename="NO_DATA_ARCHIWUM_{datetime.now()}.csv"'

    return response


# Class based views
class LoginPage(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


class Logout(LogoutView):
    next_page = 'login'


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'base/home.html'
    login_url = '/login/'


class CreateIncomming(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_incomming.html'
    login_url = '/login/'


class CreateSingleIncomming(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_single_incomming.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = IncommingShoeForm

        return context

    def post(self, request, *args, **kwargs):
        form = IncommingShoeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Pomyślnie utworzono nadchodzącą przesyłkę!')
            return redirect('create-incomming')
        else:
            messages.error(
                request, 'Podczas tworzenia nadchodzącej przesyłki wystąpił błąd!')
            return redirect('create-single-incomming')


class CreateIncommingCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_incomming_csv.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InputCsvForm()

        return context

    def post(self, request, *args, **kwargs):
        form = InputCsvForm(request.POST, request.FILES)
        if form.is_valid():
            added = not_added = 0
            added_ids = []
            not_added_line_nr = []

            file = request.FILES['file'].read().decode('utf-8-sig')

            incommings = file.strip().replace('\r', '').split('\n')

            for nr, incomming in enumerate(incommings[1:]):
                line = incomming.split(';')

                if len(line) == 11:
                    try:
                        new_incomming = IncommingShoe.objects.create(
                            order_date=line[0],
                            buy_invoice_date=line[1] if line[1] else None,
                            name=line[2],
                            size=line[3],
                            cw=line[4],
                            seller=Seller.objects.get(name=line[5]),
                            buy_invoice_nr=line[6],
                            order_nr=line[7],
                            email=line[8],
                            buy_price=line[9],
                            comment=line[10],
                        )

                        added += 1
                        added_ids.append(new_incomming.id)
                    except:
                        not_added += 1
                        not_added_line_nr.append(nr + 1)
                else:
                    not_added += 1
                    not_added_line_nr.append(nr + 1)

            messages.success(
                request, f'Pomyślnie utworzono nadchodzące przesyłki! {added} zostało utworzonych, {not_added} nie zostało utworzonych!')

            query = '?'
            for added_id in added_ids:
                query = query + 'ad=' + str(added_id) + '&'

            for line_nr in not_added_line_nr:
                query = query + 'nad=' + str(line_nr) + '&'

            query = query[:-1]

            return redirect(reverse('created-incommings') + query)

        else:
            messages.error(
                request, 'Podczas tworzenia nadchodzących przesyłek wystąpił błąd! Dostępne formaty plików to: csv, xls, xlsx!')

        return redirect('create-incomming-csv')


class CreatedIncommings(LoginRequiredMixin, TemplateView):
    template_name = 'base/created_incommings.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created_ids = self.request.GET.getlist('ad')
        context['created_incommings'] = IncommingShoe.objects.filter(
            id__in=created_ids)
        context['not_created'] = self.request.GET.getlist('nad')

        return context


class CheckIncomming(LoginRequiredMixin, ListView):
    template_name = 'base/check_incomming.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        incommings = IncommingShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            incommings = incommings.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            incommings = incommings.filter(
                seller__name__contains=seller)

        order_nr = self.request.GET.get('on')
        if order_nr:
            incommings = incommings.filter(
                order_nr__contains=order_nr)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            incommings = incommings.filter(
                order_date=order_date)

        return sorted(incommings, key=attrgetter('order_date'))


class EntryIn(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in.html'
    login_url = '/login/'


class EntryInSingle(LoginRequiredMixin, ListView):
    template_name = 'base/entry_in_single.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        incommings = IncommingShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            incommings = incommings.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            incommings = incommings.filter(
                seller__name__contains=seller)

        order_nr = self.request.GET.get('on')
        if order_nr:
            incommings = incommings.filter(
                order_nr__contains=order_nr)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            incommings = incommings.filter(
                order_date=order_date)

        return sorted(incommings, key=attrgetter('order_date'))


class CreateSingleEntryIn(LoginRequiredMixin, DetailView):
    template_name = 'base/create_single_entry_in.html'
    login_url = '/login/'
    model = IncommingShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EntryInForm
        context['incomming'] = IncommingShoe.objects.get(
            id=self.get_object().pk)

        max_storage_nr_storage = InStorageShoe.objects.aggregate(
            Max('storage_nr'))
        max_storage_nr_archives = SoldShoe.objects.aggregate(Max('storage_nr'))

        if max_storage_nr_storage['storage_nr__max'] and max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max(
                [max_storage_nr_storage['storage_nr__max'], max_storage_nr_archives['storage_nr__max']])
        elif max_storage_nr_storage['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_storage['storage_nr__max']
        elif max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_archives['storage_nr__max']
        else:
            context['max_storage_nr'] = 0

        return context

    def post(self, request, *args, **kwargs):
        form = EntryInForm(request.POST)
        if form.is_valid():
            try:
                SoldShoe.objects.get(
                    storage_nr=form.cleaned_data['storage_nr'])

                messages.error(
                    request, 'Podczas przyjmowania przesyłki na magazyn wystąpił błąd!')
                messages.error(
                    request, 'Sprawdź czy numer magazynowy nie istnieje już na magazynie!')

                return redirect('create-single-entry-in', pk=self.get_object().pk)

            except:
                pass

            try:
                incomming_shoe = IncommingShoe.objects.get(
                    id=self.get_object().pk)

                in_storage_shoe = InStorageShoe.objects.create(
                    storage_nr=form.cleaned_data['storage_nr'],
                    entry_date=form.cleaned_data['entry_date'],
                    buy_invoice_date=incomming_shoe.buy_invoice_date,
                    name=incomming_shoe.name,
                    size=incomming_shoe.size,
                    cw=incomming_shoe.cw,
                    seller=incomming_shoe.seller,
                    buy_invoice_nr=incomming_shoe.buy_invoice_nr,
                    order_nr=incomming_shoe.order_nr,
                    email=incomming_shoe.email,
                    buy_price=incomming_shoe.buy_price,
                    comment=incomming_shoe.comment,
                )

                incomming_shoe.delete()

                messages.success(
                    request, f'Pomyślnie przyjęto przesyłkę na magazyn! Numer magazynowy przesyłki to: {in_storage_shoe.storage_nr}')
                return redirect('entry-in-single')
            except:
                pass

        messages.error(
            request, 'Podczas przyjmowania przesyłki na magazyn wystąpił błąd!')

        if 'storage_nr' in form.errors.as_data().keys():
            messages.error(
                request, 'Sprawdź czy numer magazynowy nie istnieje już na magazynie!')

        return redirect('create-single-entry-in', pk=self.get_object().pk)


class EntryInCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in_csv.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InputCsvForm()

        max_storage_nr_storage = InStorageShoe.objects.aggregate(
            Max('storage_nr'))

        max_storage_nr_archives = SoldShoe.objects.aggregate(
            Max('storage_nr'))

        if max_storage_nr_storage['storage_nr__max'] and max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max(
                [max_storage_nr_storage['storage_nr__max'], max_storage_nr_archives['storage_nr__max']])
        elif max_storage_nr_storage['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_storage['storage_nr__max']
        elif max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_archives['storage_nr__max']
        else:
            context['max_storage_nr'] = 0

        return context

    def post(self, request, *args, **kwargs):
        form = InputCsvForm(request.POST, request.FILES)
        if form.is_valid():
            added = not_added = 0
            added_ids = []
            not_added_line_nr = []

            file = request.FILES['file'].read().decode('utf-8-sig')

            entry_ins = file.strip().replace('\r', '').split('\n')

            for nr, entry_in in enumerate(entry_ins[1:]):
                line = entry_in.split(';')

                if len(line) == 12:
                    try:
                        incommings = IncommingShoe.objects.filter(
                            buy_invoice_date=line[2] if line[2] else None,
                            name=line[3],
                            size=line[4],
                            cw=line[5],
                            seller=Seller.objects.get(name=line[6]),
                            buy_invoice_nr=line[7],
                            order_nr=line[8],
                            email=line[9],
                            buy_price=line[10],
                            comment=line[11],
                        )

                        if incommings:
                            incomming = incommings.first()

                            new_entry_in = InStorageShoe.objects.create(
                                storage_nr=line[0],
                                entry_date=line[1],
                                buy_invoice_date=line[2] if line[2] else None,
                                name=line[3],
                                size=line[4],
                                cw=line[5],
                                seller=Seller.objects.get(name=line[6]),
                                buy_invoice_nr=line[7],
                                order_nr=line[8],
                                email=line[9],
                                buy_price=line[10],
                                comment=line[11],
                            )

                            incomming.delete()

                            added += 1
                            added_ids.append(new_entry_in.id)
                        else:
                            not_added += 1
                            not_added_line_nr.append(nr + 1)
                    except:
                        not_added += 1
                        not_added_line_nr.append(nr + 1)
                else:
                    not_added += 1
                    not_added_line_nr.append(nr + 1)

            messages.success(
                request, f'Pomyślnie przyjęto nadchodzące przesyłki! {added} zostało przyjętych, {not_added} nie zostało przyjętych!')

            query = '?'
            for added_id in added_ids:
                query = query + 'ad=' + str(added_id) + '&'

            for line_nr in not_added_line_nr:
                query = query + 'nad=' + str(line_nr) + '&'

            query = query[:-1]

            return redirect(reverse('created-entry-ins') + query)

        else:
            messages.error(
                request, 'Podczas przyjmowania nadchodzących przesyłek wystąpił błąd! Dostępne formaty plików to: csv, xls, xlsx!')

        return redirect('entry-in-csv')


class AddToStorageCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in_csv.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InputCsvForm()

        max_storage_nr_storage = InStorageShoe.objects.aggregate(
            Max('storage_nr'))
        max_storage_nr_archives = SoldShoe.objects.aggregate(Max('storage_nr'))

        if max_storage_nr_storage['storage_nr__max'] and max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max(
                [max_storage_nr_storage['storage_nr__max'], max_storage_nr_archives['storage_nr__max']])
        elif max_storage_nr_storage['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_storage['storage_nr__max']
        elif max_storage_nr_archives['storage_nr__max']:
            context['max_storage_nr'] = max_storage_nr_archives['storage_nr__max']
        else:
            context['max_storage_nr'] = 0

        return context

    def post(self, request, *args, **kwargs):
        form = InputCsvForm(request.POST, request.FILES)
        if form.is_valid():
            added = not_added = 0
            added_ids = []
            not_added_line_nr = []

            file = request.FILES['file'].read().decode('utf-8-sig')

            entry_ins = file.strip().replace('\r', '').split('\n')

            for nr, entry_in in enumerate(entry_ins[1:]):
                line = entry_in.split(';')

                if len(line) == 12:
                    try:
                        new_entry_in = InStorageShoe.objects.create(
                            storage_nr=line[0],
                            entry_date=line[1],
                            buy_invoice_date=line[2] if line[2] else None,
                            name=line[3],
                            size=line[4],
                            cw=line[5],
                            seller=Seller.objects.get(name=line[6]),
                            buy_invoice_nr=line[7],
                            order_nr=line[8],
                            email=line[9],
                            buy_price=line[10],
                            comment=line[11],
                        )

                        added += 1
                        added_ids.append(new_entry_in.id)
                    except:
                        not_added += 1
                        not_added_line_nr.append(nr + 1)
                else:
                    not_added += 1
                    not_added_line_nr.append(nr + 1)

            messages.success(
                request, f'Pomyślnie dodano przesyłki do magazynu! {added} zostało dodanych, {not_added} nie zostało dodanych!')

            query = '?'
            for added_id in added_ids:
                query = query + 'ad=' + str(added_id) + '&'

            for line_nr in not_added_line_nr:
                query = query + 'nad=' + str(line_nr) + '&'

            query = query[:-1]

            return redirect(reverse('created-entry-ins') + query)

        else:
            messages.error(
                request, 'Podczas dodawania przesyłek do magazynu wystąpił błąd! Dostępne formaty plików to: csv, xls, xlsx!')

        return redirect('add-to-storage-csv')


class CreatedEntryIns(LoginRequiredMixin, TemplateView):
    template_name = 'base/created_entry_ins.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created_ids = self.request.GET.getlist('ad')
        context['created_entry_ins'] = InStorageShoe.objects.filter(
            id__in=created_ids)
        context['not_created'] = self.request.GET.getlist('nad')

        return context


class CheckStorage(LoginRequiredMixin, ListView):
    template_name = 'base/check_storage.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        in_storage = InStorageShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            in_storage = in_storage.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            in_storage = in_storage.filter(
                seller__name__contains=seller)

        order_nr = self.request.GET.get('on')
        if order_nr:
            in_storage = in_storage.filter(
                order_nr__contains=order_nr)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            in_storage = in_storage.filter(
                entry_date=entry_date)

        return sorted(in_storage, key=lambda x: x.storage_nr if x.storage_nr else 0)


class Send(LoginRequiredMixin, TemplateView):
    template_name = 'base/send.html'
    login_url = '/login/'


class SendSingle(LoginRequiredMixin, ListView):
    template_name = 'base/send_single.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self, **kwargs):
        in_storage = InStorageShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            in_storage = in_storage.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            in_storage = in_storage.filter(
                seller__name__contains=seller)

        order_nr = self.request.GET.get('on')
        if order_nr:
            in_storage = in_storage.filter(
                order_nr__contains=order_nr)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            in_storage = in_storage.filter(
                entry_date=entry_date)

        return sorted(in_storage, key=lambda x: x.storage_nr if x.storage_nr else 0)


class CreateSingleSend(LoginRequiredMixin, DetailView):
    template_name = 'base/create_single_send.html'
    login_url = '/login/'
    model = InStorageShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SendForm
        context['in_storage'] = InStorageShoe.objects.get(
            id=self.get_object().pk)

        return context

    def post(self, request, *args, **kwargs):
        form = SendForm(request.POST)
        if form.is_valid():
            try:
                in_storage_shoe = InStorageShoe.objects.get(
                    id=self.get_object().pk)

                sold_shoe = SoldShoe.objects.create(
                    storage_nr=in_storage_shoe.storage_nr,
                    entry_date=in_storage_shoe.entry_date,
                    exit_date=form.cleaned_data['exit_date'],
                    buy_invoice_date=in_storage_shoe.buy_invoice_date,
                    sell_invoice_date=form.cleaned_data['sell_invoice_date'],
                    money_income_date=form.cleaned_data['money_income_date'],
                    stockx_invoice_date=form.cleaned_data['stockx_invoice_date'],
                    name=in_storage_shoe.name,
                    size=in_storage_shoe.size,
                    cw=in_storage_shoe.cw,
                    stockx_nr=form.cleaned_data['stockx_nr'] if form.cleaned_data['stockx_nr'] is not None else "",
                    sell_invoice_nr=form.cleaned_data['sell_invoice_nr'] if form.cleaned_data[
                        'sell_invoice_nr'] is not None else "",
                    tracking_nr=form.cleaned_data['tracking_nr'] if form.cleaned_data['tracking_nr'] is not None else "",
                    seller=in_storage_shoe.seller,
                    buy_invoice_nr=in_storage_shoe.buy_invoice_nr,
                    order_nr=in_storage_shoe.order_nr,
                    email=in_storage_shoe.email,
                    buy_price=in_storage_shoe.buy_price,
                    sell_price=form.cleaned_data['sell_price'] if form.cleaned_data['sell_price'] is not None else 0,
                    eur_alias=form.cleaned_data['eur_alias'] if form.cleaned_data['eur_alias'] is not None else 0,
                    buyer=form.cleaned_data['buyer'],
                    comment=in_storage_shoe.comment,
                    exchange_rate=form.cleaned_data['exchange_rate'] if form.cleaned_data['exchange_rate'] is not None else 0,
                )

                in_storage_shoe.delete()

                messages.success(
                    request, f'Pomyślnie wysłano przesyłkę! Numer magazynowy przesyłki: {sold_shoe.storage_nr}')
                return redirect('send-single')

            except IntegrityError:
                messages.error(
                    request, 'Sprawdź czy numer magazynowy nie istnieje już na magazynie!')
            except:
                pass

        messages.error(
            request, 'Podczas wysyłania przesyłki wystąpił błąd!')
        return redirect('create-single-send', pk=self.get_object().pk)


class CreateSendCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_send_csv.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InputCsvForm()

        return context

    def post(self, request, *args, **kwargs):
        form = InputCsvForm(request.POST, request.FILES)
        if form.is_valid():
            added = not_added = 0
            added_ids = []
            not_added_line_nr = []

            file = request.FILES['file'].read().decode('utf-8-sig')

            sends = file.strip().replace('\r', '').split('\n')

            for nr, send in enumerate(sends[1:]):
                line = send.split(';')

                if len(line) == 23:
                    try:
                        in_storage = InStorageShoe.objects.get(
                            storage_nr=line[0],
                            entry_date=line[1],
                            buy_invoice_date=line[3] if line[3] else None,
                            name=line[7],
                            size=line[8],
                            cw=line[9],
                            seller=Seller.objects.get(name=line[13]),
                            buy_invoice_nr=line[14],
                            order_nr=line[15],
                            email=line[16],
                            buy_price=line[17],
                            comment=line[21],
                        )

                        if in_storage:
                            new_send = SoldShoe.objects.create(
                                storage_nr=line[0],
                                entry_date=line[1],
                                exit_date=line[2],
                                buy_invoice_date=line[3] if line[3] else None,
                                sell_invoice_date=line[4] if line[4] else None,
                                money_income_date=line[5] if line[5] else None,
                                stockx_invoice_date=line[6] if line[6] else None,
                                name=line[7],
                                size=line[8],
                                cw=line[9] if line[9] else '',
                                stockx_nr=line[10] if line[10] else '',
                                sell_invoice_nr=line[11] if line[11] else '',
                                tracking_nr=line[12] if line[12] else '',
                                seller=Seller.objects.get(name=line[13]),
                                buy_invoice_nr=line[14] if line[14] else '',
                                order_nr=line[15] if line[15] else '',
                                email=line[16],
                                buy_price=line[17],
                                sell_price=line[18] if line[18] else 0,
                                eur_alias=line[19] if line[19] else 0,
                                buyer=Buyer.objects.get(
                                    name=line[20]) if line[20] else None,
                                comment=line[21] if line[21] else '',
                                exchange_rate=line[22] if line[22] else 0,
                            )

                            in_storage.delete()

                            added += 1
                            added_ids.append(new_send.id)
                        else:
                            not_added += 1
                            not_added_line_nr.append(nr + 1)
                    except Exception as e:
                        print(e)
                        not_added += 1
                        not_added_line_nr.append(nr + 1)
                else:
                    not_added += 1
                    not_added_line_nr.append(nr + 1)

            messages.success(
                request, f'Pomyślnie wysłano przesyłki! {added} zostało wysłanych, {not_added} nie zostało wysłanych!')

            query = '?'
            for added_id in added_ids:
                query = query + 'ad=' + str(added_id) + '&'

            for line_nr in not_added_line_nr:
                query = query + 'nad=' + str(line_nr) + '&'

            query = query[:-1]

            return redirect(reverse('created-sends') + query)

        else:
            messages.error(
                request, 'Podczas tworzenia wysyłania przesyłek wystąpił błąd! Dostępne formaty plików to: csv, xls, xlsx!')

        return redirect('create-send-csv')


class AddToArchivesCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_send_csv.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InputCsvForm()

        return context

    def post(self, request, *args, **kwargs):
        form = InputCsvForm(request.POST, request.FILES)
        if form.is_valid():
            added = not_added = 0
            added_ids = []
            not_added_line_nr = []

            file = request.FILES['file'].read().decode('utf-8-sig')

            sends = file.strip().replace('\r', '').split('\n')

            for nr, send in enumerate(sends[1:]):
                line = send.split(';')

                if len(line) == 23:
                    try:
                        new_send = SoldShoe.objects.create(
                            storage_nr=line[0],
                            entry_date=line[1],
                            exit_date=line[2] if line[2] else None,
                            buy_invoice_date=line[3] if line[3] else None,
                            sell_invoice_date=line[4] if line[4] else None,
                            money_income_date=line[5] if line[5] else None,
                            stockx_invoice_date=line[6] if line[6] else None,
                            name=line[7],
                            size=line[8],
                            cw=line[9],
                            stockx_nr=line[10],
                            sell_invoice_nr=line[11],
                            tracking_nr=line[12],
                            seller=Seller.objects.get(name=line[13]),
                            buy_invoice_nr=line[14],
                            order_nr=line[15],
                            email=line[16],
                            buy_price=line[17],
                            sell_price=line[18] if line[18] else 0,
                            eur_alias=line[19] if line[19] else 0,
                            buyer=Buyer.objects.get(
                                name=line[20]) if line[20] else None,
                            comment=line[21],
                            exchange_rate=line[22],
                        )

                        added += 1
                        added_ids.append(new_send.id)
                    except:
                        not_added += 1
                        not_added_line_nr.append(nr + 1)
                else:
                    not_added += 1
                    not_added_line_nr.append(nr + 1)

            messages.success(
                request, f'Pomyślnie dodano przesyłki do archiwum! {added} zostało dodanych, {not_added} nie zostało dodanych!')

            query = '?'
            for added_id in added_ids:
                query = query + 'ad=' + str(added_id) + '&'

            for line_nr in not_added_line_nr:
                query = query + 'nad=' + str(line_nr) + '&'

            query = query[:-1]

            return redirect(reverse('created-sends') + query)

        else:
            messages.error(
                request, 'Podczas dodawania przesyłek do archiwum wystąpił błąd! Dostępne formaty plików to: csv, xls, xlsx!')

        return redirect('add-to-archives-csv')


class CreatedSends(LoginRequiredMixin, TemplateView):
    template_name = 'base/created_sends.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        created_ids = self.request.GET.getlist('ad')
        context['created_sends'] = SoldShoe.objects.filter(
            id__in=created_ids)
        context['not_created'] = self.request.GET.getlist('nad')

        return context


class Archives(LoginRequiredMixin, ListView):
    template_name = 'base/archives.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        sold_shoes = SoldShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            sold_shoes = sold_shoes.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            sold_shoes = sold_shoes.filter(
                seller__name__contains=seller)

        buyer = self.request.GET.get('b')
        if buyer:
            sold_shoes = sold_shoes.filter(
                buyer__name__contains=buyer)

        order_nr = self.request.GET.get('on')
        if order_nr:
            sold_shoes = sold_shoes.filter(
                order_nr__contains=order_nr)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            sold_shoes = sold_shoes.filter(
                entry_date=entry_date)

        send_date = self.request.GET.get('sd')
        if send_date:
            send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
            sold_shoes = sold_shoes.filter(
                exit_date=send_date)

        return sorted(sold_shoes, key=lambda x: x.storage_nr if x.storage_nr else 0)


class InputMissingData(LoginRequiredMixin, TemplateView):
    template_name = 'base/input_missing_data.html'
    login_url = '/login/'


class InputMissingArchives(LoginRequiredMixin, ListView):
    template_name = 'base/input_missing_archives.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        missing_data_archives = SoldShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True) |
            Q(sell_invoice_nr__exact='') | Q(sell_invoice_date__isnull=True) |
            Q(money_income_date__isnull=True) | Q(sell_price__isnull=True) |
            Q(buyer__isnull=True) | Q(tracking_nr__exact='') |
            Q(stockx_nr__exact='') | Q(cw__exact=''))

        name = self.request.GET.get('n')
        if name:
            missing_data_archives = missing_data_archives.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            missing_data_archives = missing_data_archives.filter(
                seller__name__contains=seller)

        buyer = self.request.GET.get('b')
        if buyer:
            missing_data_archives = missing_data_archives.filter(
                buyer__name__contains=buyer)

        order_nr = self.request.GET.get('on')
        if order_nr:
            missing_data_archives = missing_data_archives.filter(
                order_nr__contains=order_nr)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            missing_data_archives = missing_data_archives.filter(
                entry_date=entry_date)

        send_date = self.request.GET.get('sd')
        if send_date:
            send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
            missing_data_archives = missing_data_archives.filter(
                exit_date=send_date)

        return sorted(missing_data_archives, key=lambda x: x.storage_nr if x.storage_nr else 0)


class InputMissingStorage(LoginRequiredMixin, ListView):
    template_name = 'base/input_missing_storage.html'
    login_url = '/login/'
    paginate_by = 25

    def get_queryset(self):
        missing_data_storage = InStorageShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True))

        name = self.request.GET.get('n')
        if name:
            missing_data_storage = missing_data_storage.filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            missing_data_storage = missing_data_storage.filter(
                seller__name__contains=seller)

        order_nr = self.request.GET.get('on')
        if order_nr:
            missing_data_storage = missing_data_storage.filter(
                order_nr__contains=order_nr)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            missing_data_storage = missing_data_storage.filter(
                entry_date=entry_date)

        return sorted(missing_data_storage, key=lambda x: x.storage_nr if x.storage_nr else 0)


class InputDataArchives(LoginRequiredMixin, DetailView):
    template_name = 'base/input_data_archives.html'
    login_url = '/login/'
    model = SoldShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sold_shoe = SoldShoe.objects.get(id=self.get_object().pk)

        context['sold_shoe'] = sold_shoe
        context['form'] = SoldMissingForm(instance=sold_shoe)
        context['input_missing'] = True

        return context

    def post(self, request, *args, **kwargs):
        form = SoldMissingForm(request.POST)

        if form.is_valid():
            sold_shoe = SoldShoe.objects.get(id=self.get_object().pk)
            if sold_shoe:
                sold_shoe.entry_date = form.cleaned_data['entry_date']
                sold_shoe.exit_date = form.cleaned_data['exit_date']
                sold_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']
                sold_shoe.sell_invoice_date = form.cleaned_data['sell_invoice_date']
                sold_shoe.money_income_date = form.cleaned_data['money_income_date']
                sold_shoe.stockx_invoice_date = form.cleaned_data['stockx_invoice_date']
                sold_shoe.name = form.cleaned_data['name']
                sold_shoe.size = form.cleaned_data['size']
                sold_shoe.cw = form.cleaned_data['cw']
                sold_shoe.stockx_nr = form.cleaned_data['stockx_nr']
                sold_shoe.sell_invoice_nr = form.cleaned_data['sell_invoice_nr']
                sold_shoe.tracking_nr = form.cleaned_data['tracking_nr']
                sold_shoe.seller = form.cleaned_data['seller']
                sold_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                sold_shoe.order_nr = form.cleaned_data['order_nr']
                sold_shoe.email = form.cleaned_data['email']
                sold_shoe.buy_price = form.cleaned_data['buy_price']
                sold_shoe.sell_price = form.cleaned_data['sell_price']
                sold_shoe.eur_alias = form.cleaned_data['eur_alias']
                sold_shoe.buyer = form.cleaned_data['buyer']
                sold_shoe.comment = form.cleaned_data['comment']
                sold_shoe.exchange_rate = form.cleaned_data['exchange_rate']

                sold_shoe.save()

                messages.success(
                    request, f'Pomyślnie uzupełniono dane! Numer magazynowy przesyłki to: {sold_shoe.storage_nr}')
                return redirect('input-missing-archives')

        messages.error(
            request, 'Podczas aktualizowania danych wystąpił błąd!')
        return redirect('input-data-archives', pk=self.get_object().pk)


class InputDataStorage(LoginRequiredMixin, DetailView):
    template_name = 'base/input_data_storage.html'
    login_url = '/login/'
    model = InStorageShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        in_storage_shoe = InStorageShoe.objects.get(id=self.get_object().pk)

        context['in_storage_shoe'] = in_storage_shoe
        context['form'] = InStorageMissingForm(instance=in_storage_shoe)
        context['input_missing'] = True

        return context

    def post(self, request, *args, **kwargs):
        form = InStorageMissingForm(request.POST)

        if form.is_valid():
            in_storage_shoe = InStorageShoe.objects.get(
                id=self.get_object().pk)

            if in_storage_shoe:
                in_storage_shoe.entry_date = form.cleaned_data['entry_date']
                in_storage_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']
                in_storage_shoe.name = form.cleaned_data['name']
                in_storage_shoe.size = form.cleaned_data['size']
                in_storage_shoe.cw = form.cleaned_data['cw']
                in_storage_shoe.seller = form.cleaned_data['seller']
                in_storage_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                in_storage_shoe.order_nr = form.cleaned_data['order_nr']
                in_storage_shoe.email = form.cleaned_data['email']
                in_storage_shoe.buy_price = form.cleaned_data['buy_price']
                in_storage_shoe.comment = form.cleaned_data['comment']

                in_storage_shoe.save()

                messages.success(
                    request, f'Pomyślnie uzupełniono dane! Numer magazynowy przesyłki to: {in_storage_shoe.storage_nr}')
                return redirect('input-missing-storage')

        messages.error(
            request, 'Podczas aktualizowania danych wystąpił błąd!')

        return redirect('input-data-storage', pk=self.get_object().pk)


class EditIncomming(LoginRequiredMixin, DetailView):
    template_name = 'base/input_data_incomming.html'
    login_url = '/login/'
    model = IncommingShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        incomming_shoe = IncommingShoe.objects.get(id=self.get_object().pk)

        context['incomming_shoe'] = incomming_shoe
        context['form'] = IncommingShoeForm(instance=incomming_shoe)

        return context

    def post(self, request, *args, **kwargs):
        form = IncommingShoeForm(request.POST)

        if form.is_valid():
            incomming_shoe = IncommingShoe.objects.get(id=self.get_object().pk)
            if incomming_shoe:
                incomming_shoe.order_date = form.cleaned_data['order_date']
                incomming_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']
                incomming_shoe.name = form.cleaned_data['name']
                incomming_shoe.size = form.cleaned_data['size']
                incomming_shoe.cw = form.cleaned_data['cw']
                incomming_shoe.seller = form.cleaned_data['seller']
                incomming_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                incomming_shoe.order_nr = form.cleaned_data['order_nr']
                incomming_shoe.email = form.cleaned_data['email']
                incomming_shoe.buy_price = form.cleaned_data['buy_price']
                incomming_shoe.comment = form.cleaned_data['comment']

                incomming_shoe.save()

                messages.success(
                    request, f'Pomyślnie edytowano nadchodzącą przesyłkę! ID przesyłki to: {incomming_shoe.id}')
                return redirect('check-incomming')

        messages.error(
            request, 'Podczas aktualizowania danych wystąpił błąd!')
        return redirect('input-data-archives', pk=self.get_object().pk)


class DeleteIncomming(LoginRequiredMixin, TemplateView):
    template_name = 'base/delete_incomming.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['incomming_shoe'] = IncommingShoe.objects.get(id=kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        try:
            incomming_shoe = IncommingShoe.objects.get(id=kwargs['pk'])
            incomming_shoe.delete()

            messages.success(
                request, 'Pomyślnie usunięto nadchodzącą przesyłkę!')
            return redirect('check-incomming')
        except:
            messages.error(
                request, 'Nie udało się usunąć nadchodzącej przesyłki!')
            return redirect('delete-incomming', pk=self.get_object().pk)


class EditStorage(LoginRequiredMixin, DetailView):
    template_name = 'base/input_data_storage.html'
    login_url = '/login/'
    model = InStorageShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        in_storage_shoe = InStorageShoe.objects.get(id=self.get_object().pk)

        context['in_storage_shoe'] = in_storage_shoe
        context['form'] = InStorageMissingForm(instance=in_storage_shoe)
        context['input_missing'] = False

        return context

    def post(self, request, *args, **kwargs):
        form = InStorageMissingForm(request.POST)

        if form.is_valid():
            in_storage_shoe = InStorageShoe.objects.get(
                id=self.get_object().pk)

            if in_storage_shoe:
                in_storage_shoe.entry_date = form.cleaned_data['entry_date']
                in_storage_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']
                in_storage_shoe.name = form.cleaned_data['name']
                in_storage_shoe.size = form.cleaned_data['size']
                in_storage_shoe.cw = form.cleaned_data['cw']
                in_storage_shoe.seller = form.cleaned_data['seller']
                in_storage_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                in_storage_shoe.order_nr = form.cleaned_data['order_nr']
                in_storage_shoe.email = form.cleaned_data['email']
                in_storage_shoe.buy_price = form.cleaned_data['buy_price']
                in_storage_shoe.comment = form.cleaned_data['comment']

                in_storage_shoe.save()

                messages.success(
                    request, f'Pomyślnie edytowano przesyłkę w magazynie! Numer magazynowy przesyłki to: {in_storage_shoe.storage_nr}')
                return redirect('check-storage')

        messages.error(
            request, 'Podczas edytowania przesyłki na magazynie wystąpił błąd!')

        if 'storage_nr' in form.errors.as_data().keys():
            messages.error(
                request, 'Sprawdź czy numer magazynowy nie istnieje już na magazynie!')

        return redirect('edit-storage', pk=self.get_object().pk)


class DeleteStorage(LoginRequiredMixin, TemplateView):
    template_name = 'base/delete_storage.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['in_storage_shoe'] = InStorageShoe.objects.get(id=kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        try:
            in_storage_shoe = InStorageShoe.objects.get(id=kwargs['pk'])
            storage_nr = in_storage_shoe.id
            in_storage_shoe.delete()

            messages.success(
                request, f'Pomyślnie usunięto przesyłkę z magazynu! Numer magazynowy przesyłki: {storage_nr}')
            return redirect('check-storage')
        except:
            messages.error(
                request, 'Nie udało się usunąć przesyłki z magazynu!')
            return redirect('delete-storage', pk=self.get_object().pk)


class EditArchives(LoginRequiredMixin, DetailView):
    template_name = 'base/input_data_archives.html'
    login_url = '/login/'
    model = SoldShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sold_shoe = SoldShoe.objects.get(id=self.get_object().pk)

        context['sold_shoe'] = sold_shoe
        context['form'] = SoldMissingForm(instance=sold_shoe)
        context['input_missing'] = False

        return context

    def post(self, request, *args, **kwargs):
        form = SoldMissingForm(request.POST)

        if form.is_valid():
            sold_shoe = SoldShoe.objects.get(id=self.get_object().pk)
            if sold_shoe:
                sold_shoe.entry_date = form.cleaned_data['entry_date']
                sold_shoe.exit_date = form.cleaned_data['exit_date']
                sold_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']
                sold_shoe.sell_invoice_date = form.cleaned_data['sell_invoice_date']
                sold_shoe.money_income_date = form.cleaned_data['money_income_date']
                sold_shoe.stockx_invoice_date = form.cleaned_data['stockx_invoice_date']
                sold_shoe.name = form.cleaned_data['name']
                sold_shoe.size = form.cleaned_data['size']
                sold_shoe.cw = form.cleaned_data['cw']
                sold_shoe.stockx_nr = form.cleaned_data['stockx_nr']
                sold_shoe.sell_invoice_nr = form.cleaned_data['sell_invoice_nr']
                sold_shoe.tracking_nr = form.cleaned_data['tracking_nr']
                sold_shoe.seller = form.cleaned_data['seller']
                sold_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                sold_shoe.order_nr = form.cleaned_data['order_nr']
                sold_shoe.email = form.cleaned_data['email']
                sold_shoe.buy_price = form.cleaned_data['buy_price']
                sold_shoe.sell_price = form.cleaned_data['sell_price']
                sold_shoe.eur_alias = form.cleaned_data['eur_alias']
                sold_shoe.buyer = form.cleaned_data['buyer']
                sold_shoe.comment = form.cleaned_data['comment']
                sold_shoe.exchange_rate = form.cleaned_data['exchange_rate']

                sold_shoe.save()

                messages.success(
                    request, f'Pomyślnie edytowano przesyłkę w archiwum! Numer magazynowy przesyłki to: {sold_shoe.storage_nr}')
                return redirect('archives')

        messages.error(
            request, 'Podczas edytowania przesyłki w archiwum wystąpił błąd!')

        if 'storage_nr' in form.errors.as_data().keys():
            messages.error(
                request, 'Sprawdź czy numer magazynowy nie istnieje już na magazynie!')

        return redirect('edit-archives', pk=self.get_object().pk)


class DeleteArchives(LoginRequiredMixin, TemplateView):
    template_name = 'base/delete_archives.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sold_shoe'] = SoldShoe.objects.get(id=kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        try:
            sold_shoe = SoldShoe.objects.get(id=kwargs['pk'])
            storage_nr = sold_shoe.storage_nr
            sold_shoe.delete()

            messages.success(
                request, f'Pomyślnie usunięto przesyłkę z archiwum! Numer magazynowy przesyłki: {storage_nr}')
            return redirect('archives')
        except:
            messages.error(
                request, 'Nie udało się usunąć przesyłki z archiwum!')
            return redirect('delete-archives', pk=self.get_object().pk)


class Sellers(LoginRequiredMixin, TemplateView):
    template_name = 'base/sellers.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sellers'] = Seller.objects.all()

        return context


class CreateSeller(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_seller.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = SellerForm()

        return context

    def post(self, request, *args, **kwargs):
        form = SellerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Pomyślnie utworzono sprzedawcę!')
            return redirect('sellers')
        else:
            messages.error(
                request, 'Podczas tworzenia sprzedawcy wystąpił błąd!')
            return redirect('create-seller')


class DeleteSeller(LoginRequiredMixin, TemplateView):
    template_name = 'base/delete_seller.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['seller'] = Seller.objects.get(id=kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        try:
            seller = Seller.objects.get(id=kwargs['pk'])
            seller.delete()

            messages.success(request, 'Pomyślnie usunięto sprzedawcę!')
            return redirect('sellers')
        except:
            messages.error(request, 'Nie udało się usunąć sprzedawcy!')
            return redirect('sellers')


class EditSeller(LoginRequiredMixin, DetailView):
    template_name = 'base/edit_seller.html'
    login_url = '/login/'
    model = Seller

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        seller = Seller.objects.get(id=self.get_object().pk)

        context['seller'] = seller
        context['form'] = SellerForm(instance=seller)

        return context

    def post(self, request, *args, **kwargs):
        form = SellerForm(request.POST)

        if form.is_valid():
            seller = Seller.objects.get(
                id=self.get_object().pk)
            if seller:
                seller.name = form.cleaned_data['name']

                seller.save()

                messages.success(
                    request, f'Pomyślnie edytowano sprzedawcę! Nazwa sprzedawcy to: {seller.name}')
                return redirect('sellers')

        messages.error(
            request, 'Podczas edytowania sprzedawcy wystąpił błąd!')
        return redirect('edit-seller', pk=self.get_object().pk)


class Buyers(LoginRequiredMixin, TemplateView):
    template_name = 'base/buyers.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['buyers'] = Buyer.objects.all()

        return context


class CreateBuyer(LoginRequiredMixin, TemplateView):
    template_name = 'base/create_buyer.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = BuyerForm()

        return context

    def post(self, request, *args, **kwargs):
        form = BuyerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Pomyślnie utworzono kupującego!')
            return redirect('buyers')
        else:
            messages.error(
                request, 'Podczas tworzenia kupującego wystąpił błąd!')
            return redirect('create-buyer')


class DeleteBuyer(LoginRequiredMixin, TemplateView):
    template_name = 'base/delete_buyer.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['buyer'] = Buyer.objects.get(id=kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        try:
            buyer = Buyer.objects.get(id=kwargs['pk'])
            buyer.delete()

            messages.success(request, 'Pomyślnie usunięto kupującego!')
            return redirect('buyers')
        except:
            messages.error(request, 'Nie udało się usunąć kupującego!')
            return redirect('buyers')


class EditBuyer(LoginRequiredMixin, DetailView):
    template_name = 'base/edit_buyer.html'
    login_url = '/login/'
    model = Buyer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        buyer = Buyer.objects.get(id=self.get_object().pk)

        context['buyer'] = buyer
        context['form'] = BuyerForm(instance=buyer)

        return context

    def post(self, request, *args, **kwargs):
        form = BuyerForm(request.POST)

        if form.is_valid():
            buyer = Buyer.objects.get(
                id=self.get_object().pk)
            if buyer:
                buyer.name = form.cleaned_data['name']

                buyer.save()

                messages.success(
                    request, f'Pomyślnie edytowano kupującego! Nazwa kupującego to: {buyer.name}')
                return redirect('buyers')

        messages.error(
            request, 'Podczas edytowania kupującego wystąpił błąd!')
        return redirect('edit-buyer', pk=self.get_object().pk)


class PutOnAuction(LoginRequiredMixin, TemplateView):
    template_name = 'base/put_on_auction.html'
    login_url = '/login/'


# TODO: filters
class PutOnAuctionMultiple(LoginRequiredMixin, TemplateView):
    template_name = 'base/put_on_auction_multiple.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj_on_page = 25

        in_storage_shoes = InStorageShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            in_storage_shoes = in_storage_shoes.filter(
                name__contains=name)

        storage_nr = self.request.GET.get('s')
        if storage_nr and storage_nr.isnumeric():
            in_storage_shoes = in_storage_shoes.filter(
                storage_nr=storage_nr)

        in_storage_shoes = in_storage_shoes.filter(
            ~Q(id__in=[shoe.in_storage_shoe.id for shoe in OnAuctionShoe.objects.all()])).order_by('storage_nr')

        paginator = Paginator(in_storage_shoes, obj_on_page)

        page_number = int(self.request.GET.get(
            'page')) if self.request.GET.get('page') else 1
        page_obj = paginator.page(page_number)

        context['page_obj'] = page_obj

        MyFormSet = formset_factory(form=OnAuctionForm, extra=0)

        context['formset'] = MyFormSet(initial=[
                                       {'in_storage_shoe': in_storage_shoe} for in_storage_shoe in page_obj])

        for nr, form in enumerate(context['formset']):
            form.fields['in_storage_shoe'].queryset = in_storage_shoes[(
                page_number-1)*obj_on_page+nr: (page_number-1)*obj_on_page+nr+1]

        return context

    def post(self, request, *args, **kwargs):
        OnAuctionFormSet = formset_factory(form=OnAuctionForm, extra=0)
        formset = OnAuctionFormSet(request.POST)

        on_auction = []

        for form in formset:
            if form.is_valid():
                instance = form.save()

                on_auction.append(instance.id)
            else:
                continue

        query = '?'
        for on_auction_id in on_auction:
            query = query + 'on=' + str(on_auction_id) + '&'

        query = query[:-1]

        return redirect(reverse('send-on-auction') + query)


class CheckOnAuction(LoginRequiredMixin, TemplateView):
    template_name = 'base/check_on_auction.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj_on_page = 25

        in_storage_shoes = InStorageShoe.objects.all()
        on_auction_shoes = OnAuctionShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            in_storage_shoes = in_storage_shoes.filter(
                name__contains=name)
            on_auction_shoes = on_auction_shoes.filter(
                in_storage_shoe__name__contains=name)

        storage_nr = self.request.GET.get('s')
        if storage_nr and storage_nr.isnumeric():
            in_storage_shoes = in_storage_shoes.filter(
                storage_nr=storage_nr)
            on_auction_shoes = on_auction_shoes.filter(
                in_storage_shoe__storage_nr=storage_nr)

        in_storage_shoes = in_storage_shoes.filter(
            Q(id__in=[shoe.in_storage_shoe.id for shoe in OnAuctionShoe.objects.all()])).order_by('storage_nr')

        on_auction_shoes = on_auction_shoes.order_by(
            'in_storage_shoe__storage_nr')

        paginator = Paginator(on_auction_shoes, obj_on_page)

        page_number = int(self.request.GET.get(
            'page')) if self.request.GET.get('page') else 1
        page_obj = paginator.page(page_number)

        context['page_obj'] = page_obj

        MyFormSet = formset_factory(form=OnAuctionForm, extra=0)

        context['formset'] = MyFormSet(initial=[
                                       {'in_storage_shoe': on_auction_shoe.in_storage_shoe, 'alias_price': on_auction_shoe.alias_price,
                                        'stockx_price': on_auction_shoe.stockx_price, 'wtn_price': on_auction_shoe.wtn_price} for on_auction_shoe in page_obj])

        for nr, form in enumerate(context['formset']):
            form.fields['in_storage_shoe'].queryset = in_storage_shoes[(
                page_number-1)*obj_on_page+nr: (page_number-1)*obj_on_page+nr+1]

        return context

    def post(self, request, *args, **kwargs):
        OnAuctionFormSet = formset_factory(form=OnAuctionForm, extra=0)
        formset = OnAuctionFormSet(request.POST)

        edited = []
        deleted = []

        for nr, form in enumerate(formset):
            in_storage_form_field = f'form-{nr}-in_storage_shoe'
            alias_price_form_field = f'form-{nr}-alias_price'
            stockx_price_form_field = f'form-{nr}-stockx_price'
            wtn_price_form_field = f'form-{nr}-wtn_price'

            try:
                on_auction_shoe = OnAuctionShoe.objects.get(
                    in_storage_shoe__id=formset.data[in_storage_form_field])

                alias_price = str(on_auction_shoe.alias_price or '')
                stockx_price = str(on_auction_shoe.stockx_price or '')
                wtn_price = str(on_auction_shoe.wtn_price or '')

                if formset.data[alias_price_form_field] == alias_price and \
                        formset.data[stockx_price_form_field] == stockx_price and \
                        formset.data[wtn_price_form_field] == wtn_price:
                    continue

                if formset.data[alias_price_form_field]:
                    on_auction_shoe.alias_price = float(
                        formset.data[alias_price_form_field])
                elif not formset.data[alias_price_form_field] and on_auction_shoe.alias_price:
                    on_auction_shoe.alias_price = None

                if formset.data[stockx_price_form_field]:
                    on_auction_shoe.stockx_price = float(
                        formset.data[stockx_price_form_field])
                elif not formset.data[stockx_price_form_field] and on_auction_shoe.stockx_price:
                    on_auction_shoe.stockx_price = None

                if formset.data[wtn_price_form_field]:
                    on_auction_shoe.wtn_price = float(
                        formset.data[wtn_price_form_field])
                elif not formset.data[wtn_price_form_field] and on_auction_shoe.wtn_price:
                    on_auction_shoe.wtn_price = None

                if on_auction_shoe.alias_price or on_auction_shoe.stockx_price or on_auction_shoe.wtn_price:
                    on_auction_shoe.save()
                    edited.append(on_auction_shoe.id)
                else:
                    deleted.append(on_auction_shoe.in_storage_shoe.id)
                    on_auction_shoe.delete()

            except:
                continue

        query = '?'
        for on_auction_id in edited:
            query = query + 'ed=' + str(on_auction_id) + '&'

        for in_storage_id in deleted:
            query = query + 'del=' + str(in_storage_id) + '&'

        query = query[:-1]

        return redirect(reverse('edited-on-auction') + query)


class SendOnAuction(LoginRequiredMixin, TemplateView):
    template_name = 'base/send_on_auction.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['edit'] = False

        send_ids = self.request.GET.getlist('on')
        context['send_on_auction'] = OnAuctionShoe.objects.filter(
            id__in=send_ids)

        return context


class EditedOnAuction(LoginRequiredMixin, TemplateView):
    template_name = 'base/send_on_auction.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['edit'] = True

        send_ids = self.request.GET.getlist('ed')
        context['send_on_auction'] = OnAuctionShoe.objects.filter(
            id__in=send_ids)

        deleted_ids = self.request.GET.getlist('del')
        context['removed_from_auction'] = InStorageShoe.objects.filter(
            id__in=deleted_ids)

        return context


class Stats(LoginRequiredMixin, TemplateView):
    template_name = 'base/stats.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # DATES
        now = datetime.now()
        month = now.month
        year = now.year
        three_months_ago = now - relativedelta(months=3)
        year_ago = now - relativedelta(months=12)
        last_12_months = [
            now - relativedelta(months=i) for i in range(11, -1, -1)]

        # INCOMMING this month
        incomming_this_month = IncommingShoe.objects.filter(
            order_date__month=month, order_date__year=year)

        in_storage_this_month = InStorageShoe.objects.filter(
            buy_invoice_date__month=month, buy_invoice_date__year=year)

        archives_this_month = SoldShoe.objects.filter(
            buy_invoice_date__month=month, buy_invoice_date__year=year)

        context['bought_count'] = len(
            incomming_this_month) + len(in_storage_this_month) + len(archives_this_month)

        # SOLD this month
        sold_this_month = SoldShoe.objects.filter(
            exit_date__month=month, exit_date__year=year)

        context['sold_count'] = len(sold_this_month)

        # INCOME COSTS PROFIT this month
        income = costs = 0

        for shoe in sold_this_month:
            income += shoe.sell_price

        for shoe in incomming_this_month:
            costs += shoe.buy_price
        for shoe in in_storage_this_month:
            costs += shoe.buy_price
        for shoe in archives_this_month:
            costs += shoe.buy_price

        context['income'] = round(income, 2)
        context['costs'] = round(costs)
        context['profit'] = round(0.97 * float(income) - float(costs), 2)
        context['tax'] = round(0.03 * float(income), 2)

        # INCOME COSTS last year
        last_year = dict(zip([f'{date.month}.{date.year}' for date in last_12_months], [
            {'income': 0, 'costs': 0, 'profit': 0, 'returned_tax': 0} for _ in range(12)]))

        incomming_last_year = IncommingShoe.objects.filter(
            order_date__gte=year_ago)
        in_storage_last_year = InStorageShoe.objects.filter(
            buy_invoice_date__gte=year_ago)
        sold_last_year = SoldShoe.objects.filter(
            buy_invoice_date__gte=year_ago)

        for shoe in list(incomming_last_year):
            last_year[f'{shoe.order_date.month}.{shoe.order_date.year}']['costs'] += int(
                shoe.buy_price)

            last_year[f'{shoe.order_date.month}.{shoe.order_date.year}']['returned_tax'] += int(
                0.23 * float(shoe.buy_price))

        for shoe in list(in_storage_last_year) + list(sold_last_year):
            last_year[f'{shoe.buy_invoice_date.month}.{shoe.buy_invoice_date.year}']['costs'] += int(
                shoe.buy_price)

            last_year[f'{shoe.buy_invoice_date.month}.{shoe.buy_invoice_date.year}']['returned_tax'] += int(
                0.23 * float(shoe.buy_price))

        archives_last_year = SoldShoe.objects.filter(exit_date__gte=year_ago)

        for shoe in list(archives_last_year):
            last_year[f'{shoe.exit_date.month}.{shoe.exit_date.year}']['income'] += int(
                shoe.sell_price)

        for key, values in last_year.items():
            last_year[key]['profit'] = int(
                0.97 * values['income'] - values['costs'])

        context['last_year'] = last_year

        # BOUGHT FROM last 3 months
        bought_from_count = dict()

        incomming_last_3_months = IncommingShoe.objects.filter(
            order_date__gte=three_months_ago)
        in_storage_last_3_months = InStorageShoe.objects.filter(
            buy_invoice_date__gte=three_months_ago)
        archives_last_3_months = SoldShoe.objects.filter(
            buy_invoice_date__gte=three_months_ago)

        for shoe in list(incomming_last_3_months) + list(in_storage_last_3_months) + list(archives_last_3_months):
            if shoe.seller:
                bought_from_count[shoe.seller] = bought_from_count.get(
                    shoe.seller, 0) + 1
            else:
                bought_from_count['Nieznany'] = bought_from_count.get(
                    'Nieznany', 0) + 1

        context['bought_from'] = bought_from_count

        # SOLD TO last 3 months
        sold_to_count = dict()

        sold_last_3_months = SoldShoe.objects.filter(
            exit_date__gte=three_months_ago)

        for shoe in sold_last_3_months:
            if shoe.buyer:
                sold_to_count[shoe.buyer] = sold_to_count.get(
                    shoe.buyer, 0) + 1
            else:
                sold_to_count['Nieznany'] = sold_to_count.get(
                    'Nieznany', 0) + 1

        context['sold_to'] = sold_to_count

        return context


class Info(TemplateView):
    template_name = 'base/info.html'
