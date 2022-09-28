from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse

from .models import Buyer, InStorageShoe, IncommingShoe, Seller, SoldShoe
from .forms import IncommingShoeForm, EntryInForm, SendForm, SoldMissingForm, InStorageMissingForm, InputCsvForm, SellerForm, BuyerForm

from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv


# Function based views
@login_required(login_url='/login/')
def incomming_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="PRZYCHODZACE_{datetime.now()}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nr', 'Email', 'Cena kupna', 'Nazwa produktu',
                     'Rozmiar', 'Data zamowienia', 'Sprzedawca', 'Komentarz'])

    incomming_shoes = IncommingShoe.objects.all()

    name = request.GET.get('n')
    if name:
        incomming_shoes = incomming_shoes.filter(name__contains=name)

    seller = request.GET.get('s')
    if seller:
        incomming_shoes = incomming_shoes.filter(seller__name__contains=seller)

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        incomming_shoes = incomming_shoes.filter(order_date=order_date)

    for nr, shoe in enumerate(incomming_shoes):
        writer.writerow([nr+1, shoe.email, shoe.buy_price, shoe.name,
                         shoe.size, shoe.order_date, shoe.seller, shoe.comment])

    return response


@login_required(login_url='/login/')
def storage_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="MAGAZYN_{datetime.now()}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nr magazynowy', 'Email', 'Cena kupna', 'Nazwa produktu',
                     'Rozmiar', 'Data zamowienia', 'Sprzedawca', 'Komentarz',
                     'Data przyjecia', 'Nr faktury kupna', 'Data faktury kupna'])

    in_storage_shoes = InStorageShoe.objects.all()

    name = request.GET.get('n')
    if name:
        in_storage_shoes = in_storage_shoes.filter(name__contains=name)

    seller = request.GET.get('s')
    if seller:
        in_storage_shoes = in_storage_shoes.filter(
            seller__name__contains=seller)

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        in_storage_shoes = in_storage_shoes.filter(order_date=order_date)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        in_storage_shoes = in_storage_shoes.filter(entry_date=entry_date)

    for shoe in in_storage_shoes:
        writer.writerow([shoe.id, shoe.email, shoe.buy_price, shoe.name,
                         shoe.size, shoe.order_date, shoe.seller, shoe.comment,
                         shoe.entry_date, shoe.buy_invoice_nr, shoe.buy_invoice_date])

    return response


@login_required(login_url='/login/')
def archives_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="ARCHIWUM_{datetime.now()}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nr magazynowy', 'Email', 'Cena kupna', 'Nazwa produktu',
                     'Rozmiar', 'Data zamowienia', 'Sprzedawca', 'Komentarz',
                     'Data przyjecia', 'Nr faktury kupna', 'Data faktury kupna',
                     'Data wydania', 'Nr faktury sprzedazy', 'Data faktury sprzedazy',
                     'Data wpływu na konto', 'Cena sprzedazy', 'Kupujący',
                     'Numer listu przewozowego', 'Nr StockX', 'CW'])

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

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        sold_shoes = sold_shoes.filter(order_date=order_date)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        sold_shoes = sold_shoes.filter(entry_date=entry_date)

    send_date = request.GET.get('sd')
    if send_date:
        send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
        sold_shoes = sold_shoes.filter(exit_date=send_date)

    for shoe in sold_shoes:
        writer.writerow([shoe.storage_nr, shoe.email, shoe.buy_price, shoe.name,
                         shoe.size, shoe.order_date, shoe.seller, shoe.comment,
                         shoe.entry_date, shoe.buy_invoice_nr, shoe.buy_invoice_date,
                         shoe.exit_date, shoe.sell_invoice_nr, shoe.sell_invoice_date,
                         shoe.money_income_date, shoe.sell_price, shoe.buyer,
                         shoe.tracking_nr, shoe.stockx_nr, shoe.cw])

    return response


@login_required(login_url='/login/')
def missing_storage_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="NO_DATA_MAGAZYN_{datetime.now()}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nr magazynowy', 'Email', 'Cena kupna', 'Nazwa produktu',
                     'Rozmiar', 'Data zamowienia', 'Sprzedawca', 'Komentarz',
                     'Data przyjecia', 'Nr faktury kupna', 'Data faktury kupna'])

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

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        missing_storage = missing_storage.filter(order_date=order_date)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        missing_storage = missing_storage.filter(entry_date=entry_date)

    for shoe in missing_storage:
        writer.writerow([shoe.id, shoe.email, shoe.buy_price, shoe.name,
                         shoe.size, shoe.order_date, shoe.seller, shoe.comment,
                         shoe.entry_date, shoe.buy_invoice_nr, shoe.buy_invoice_date])

    return response


@login_required(login_url='/login/')
def missing_archives_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="NO_DATA_ARCHIWUM_{datetime.now()}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nr magazynowy', 'Email', 'Cena kupna', 'Nazwa produktu',
                     'Rozmiar', 'Data zamowienia', 'Sprzedawca', 'Komentarz',
                     'Data przyjecia', 'Nr faktury kupna', 'Data faktury kupna',
                     'Data wydania', 'Nr faktury sprzedazy', 'Data faktury sprzedazy',
                     'Data wpływu na konto', 'Cena sprzedazy', 'Kupujący',
                     'Numer listu przewozowego', 'Nr StockX', 'CW'])

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

    order_date = request.GET.get('od')
    if order_date:
        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
        missing_archives = missing_archives.filter(order_date=order_date)

    entry_date = request.GET.get('ed')
    if entry_date:
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
        missing_archives = missing_archives.filter(entry_date=entry_date)

    send_date = request.GET.get('sd')
    if send_date:
        send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
        missing_archives = missing_archives.filter(exit_date=send_date)

    for shoe in missing_archives:
        writer.writerow([shoe.storage_nr, shoe.email, shoe.buy_price, shoe.name,
                         shoe.size, shoe.order_date, shoe.seller, shoe.comment,
                         shoe.entry_date, shoe.buy_invoice_nr, shoe.buy_invoice_date,
                         shoe.exit_date, shoe.sell_invoice_nr, shoe.sell_invoice_date,
                         shoe.money_income_date, shoe.sell_price, shoe.buyer,
                         shoe.tracking_nr, shoe.stockx_nr, shoe.cw])

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

                if len(line) == 7:
                    try:
                        new_incomming = IncommingShoe.objects.create(
                            email=line[0],
                            buy_price=line[1],
                            name=line[2],
                            size=line[3],
                            order_date=line[4],
                            seller=Seller.objects.get(name=line[5]),
                            comment=line[6],
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


class CheckIncomming(LoginRequiredMixin, TemplateView):
    template_name = 'base/check_incomming.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incommings'] = IncommingShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            context['incommings'] = context['incommings'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['incommings'] = context['incommings'].filter(
                seller__name__contains=seller)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['incommings'] = context['incommings'].filter(
                order_date=order_date)

        return context


class EntryIn(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in.html'
    login_url = '/login/'


class EntryInSingle(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in_single.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incommings'] = IncommingShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            context['incommings'] = context['incommings'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['incommings'] = context['incommings'].filter(
                seller__name__contains=seller)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['incommings'] = context['incommings'].filter(
                order_date=order_date)

        return context


class CreateSingleEntryIn(LoginRequiredMixin, DetailView):
    template_name = 'base/create_single_entry_in.html'
    login_url = '/login/'
    model = IncommingShoe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EntryInForm
        context['incomming'] = IncommingShoe.objects.get(
            id=self.get_object().pk)

        return context

    def post(self, request, *args, **kwargs):
        form = EntryInForm(request.POST)
        if form.is_valid():
            try:
                incomming_shoe = IncommingShoe.objects.get(
                    id=self.get_object().pk)

                in_storage_shoe = InStorageShoe.objects.create(
                    email=incomming_shoe.email,
                    buy_price=incomming_shoe.buy_price,
                    name=incomming_shoe.name,
                    size=incomming_shoe.size,
                    order_date=incomming_shoe.order_date,
                    seller=incomming_shoe.seller,
                    comment=incomming_shoe.comment,

                    entry_date=form.cleaned_data['entry_date'],
                    buy_invoice_nr=form.cleaned_data['buy_invoice_nr'] if form.cleaned_data[
                        'buy_invoice_nr'] is not None else "",
                    buy_invoice_date=form.cleaned_data['buy_invoice_date'],
                )

                incomming_shoe.delete()

                messages.success(
                    request, f'Pomyślnie przyjęto przesyłkę na magazyn! Numer magazynowy przesyłki to: {in_storage_shoe.id}')
                return redirect('entry-in-single')
            except:
                pass

        messages.error(
            request, 'Podczas przyjmowania przesyłki na magazyn wystąpił błąd!')
        return redirect('create-single-entry-in', pk=self.get_object().pk)


class EntryInCsv(LoginRequiredMixin, TemplateView):
    template_name = 'base/entry_in_csv.html'
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

            entry_ins = file.strip().replace('\r', '').split('\n')

            for nr, entry_in in enumerate(entry_ins[1:]):
                line = entry_in.split(';')

                if len(line) == 10:
                    try:
                        incommings = IncommingShoe.objects.filter(
                            email=line[0],
                            buy_price=line[1],
                            name=line[2],
                            size=line[3],
                            order_date=line[4],
                            seller=Seller.objects.get(name=line[5]),
                            comment=line[6],
                        )

                        if incommings:
                            incomming = incommings.first()

                            new_entry_in = InStorageShoe.objects.create(
                                email=line[0],
                                buy_price=line[1],
                                name=line[2],
                                size=line[3],
                                order_date=line[4],
                                seller=Seller.objects.get(name=line[5]),
                                comment=line[6],

                                entry_date=line[7],
                                buy_invoice_nr=line[8],
                                buy_invoice_date=line[9] if line[9] else None,
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

                if len(line) == 10:
                    try:
                        new_entry_in = InStorageShoe.objects.create(
                            email=line[0],
                            buy_price=line[1],
                            name=line[2],
                            size=line[3],
                            order_date=line[4],
                            seller=Seller.objects.get(name=line[5]),
                            comment=line[6],

                            entry_date=line[7],
                            buy_invoice_nr=line[8],
                            buy_invoice_date=line[9] if line[9] else None,
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


class CheckStorage(LoginRequiredMixin, TemplateView):
    template_name = 'base/check_storage.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_storage'] = InStorageShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            context['in_storage'] = context['in_storage'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['in_storage'] = context['in_storage'].filter(
                seller__name__contains=seller)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['in_storage'] = context['in_storage'].filter(
                order_date=order_date)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            context['in_storage'] = context['in_storage'].filter(
                entry_date=entry_date)

        return context


class Send(LoginRequiredMixin, TemplateView):
    template_name = 'base/send.html'
    login_url = '/login/'


class SendSingle(LoginRequiredMixin, TemplateView):
    template_name = 'base/send_single.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_storage'] = InStorageShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            context['in_storage'] = context['in_storage'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['in_storage'] = context['in_storage'].filter(
                seller__name__contains=seller)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['in_storage'] = context['in_storage'].filter(
                order_date=order_date)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            context['in_storage'] = context['in_storage'].filter(
                entry_date=entry_date)

        return context


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
                    email=in_storage_shoe.email,
                    buy_price=in_storage_shoe.buy_price,
                    name=in_storage_shoe.name,
                    size=in_storage_shoe.size,
                    order_date=in_storage_shoe.order_date,
                    seller=in_storage_shoe.seller,
                    comment=in_storage_shoe.comment,

                    entry_date=in_storage_shoe.entry_date,
                    buy_invoice_nr=in_storage_shoe.buy_invoice_nr,
                    buy_invoice_date=in_storage_shoe.buy_invoice_date,

                    storage_nr=in_storage_shoe.id,
                    exit_date=form.cleaned_data['exit_date'],
                    sell_invoice_nr=form.cleaned_data['sell_invoice_nr'] if form.cleaned_data[
                        'sell_invoice_nr'] is not None else "",
                    sell_invoice_date=form.cleaned_data['sell_invoice_date'],
                    money_income_date=form.cleaned_data['money_income_date'],
                    sell_price=form.cleaned_data['sell_price'] if form.cleaned_data['sell_price'] is not None else 0,
                    buyer=form.cleaned_data['buyer'],
                    tracking_nr=form.cleaned_data['tracking_nr'] if form.cleaned_data['tracking_nr'] is not None else "",
                    stockx_nr=form.cleaned_data['stockx_nr'] if form.cleaned_data['stockx_nr'] is not None else "",
                    cw=form.cleaned_data['cw'] if form.cleaned_data['cw'] is not None else "",
                )

                in_storage_shoe.delete()

                messages.success(
                    request, f'Pomyślnie wysłano przesyłkę! Numer magazynowy przesyłki: {sold_shoe.storage_nr}')
                return redirect('send-single')
            except:
                pass

        messages.error(
            request, 'Podczas wysyłania przesyłki wystąpił błąd!')
        return redirect('create-single-entry-in', pk=self.get_object().pk)


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

                if len(line) == 20:
                    try:
                        in_storage = InStorageShoe.objects.get(
                            id=line[0],
                        )

                        if in_storage:
                            new_send = SoldShoe.objects.create(
                                email=line[1],
                                buy_price=line[2],
                                name=line[3],
                                size=line[4],
                                order_date=line[5],
                                seller=Seller.objects.get(name=line[6]),
                                comment=line[7],

                                entry_date=line[8],
                                buy_invoice_nr=line[9],
                                buy_invoice_date=line[10] if line[10] else None,

                                storage_nr=line[0],
                                exit_date=line[11] if line[11] else None,
                                sell_invoice_nr=line[12],
                                sell_invoice_date=line[13] if line[13] else None,
                                money_income_date=line[14] if line[14] else None,
                                sell_price=line[15],
                                buyer=Buyer.objects.get(
                                    name=line[16]) if line[16] else None,
                                tracking_nr=line[17],
                                stockx_nr=line[18],
                                cw=line[19],
                            )

                            in_storage.delete()

                            added += 1
                            added_ids.append(new_send.id)
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

                if len(line) == 20:
                    try:
                        new_send = SoldShoe.objects.create(
                            email=line[1],
                            buy_price=line[2],
                            name=line[3],
                            size=line[4],
                            order_date=line[5],
                            seller=Seller.objects.get(name=line[6]),
                            comment=line[7],

                            entry_date=line[8],
                            buy_invoice_nr=line[9],
                            buy_invoice_date=line[10] if line[10] else None,

                            storage_nr=line[0],
                            exit_date=line[11] if line[11] else None,
                            sell_invoice_nr=line[12],
                            sell_invoice_date=line[13] if line[13] else None,
                            money_income_date=line[14] if line[14] else None,
                            sell_price=line[15],
                            buyer=Buyer.objects.get(name=line[16]),
                            tracking_nr=line[17],
                            stockx_nr=line[18],
                            cw=line[19],
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


class Archives(LoginRequiredMixin, TemplateView):
    template_name = 'base/archives.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sold_shoes'] = SoldShoe.objects.all()

        name = self.request.GET.get('n')
        if name:
            context['sold_shoes'] = context['sold_shoes'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['sold_shoes'] = context['sold_shoes'].filter(
                seller__name__contains=seller)

        buyer = self.request.GET.get('b')
        if buyer:
            context['sold_shoes'] = context['sold_shoes'].filter(
                buyer__name__contains=buyer)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['sold_shoes'] = context['sold_shoes'].filter(
                order_date=order_date)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            context['sold_shoes'] = context['sold_shoes'].filter(
                entry_date=entry_date)

        send_date = self.request.GET.get('sd')
        if send_date:
            send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
            context['sold_shoes'] = context['sold_shoes'].filter(
                exit_date=send_date)

        return context


class CheckMissingData(LoginRequiredMixin, TemplateView):
    template_name = 'base/check_missing_data.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['missing_data_archives'] = SoldShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True) |
            Q(sell_invoice_nr__exact='') | Q(sell_invoice_date__isnull=True) |
            Q(money_income_date__isnull=True) | Q(sell_price__isnull=True) |
            Q(buyer__isnull=True) | Q(tracking_nr__exact='') |
            Q(stockx_nr__exact='') | Q(cw__exact=''))

        context['missing_data_storage'] = InStorageShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True))

        return context


class InputMissingData(LoginRequiredMixin, TemplateView):
    template_name = 'base/input_missing_data.html'
    login_url = '/login/'


class InputMissingArchives(LoginRequiredMixin, TemplateView):
    template_name = 'base/input_missing_archives.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['missing_data_archives'] = SoldShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True) |
            Q(sell_invoice_nr__exact='') | Q(sell_invoice_date__isnull=True) |
            Q(money_income_date__isnull=True) | Q(sell_price__isnull=True) |
            Q(buyer__isnull=True) | Q(tracking_nr__exact='') |
            Q(stockx_nr__exact='') | Q(cw__exact=''))

        name = self.request.GET.get('n')
        if name:
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                seller__name__contains=seller)

        buyer = self.request.GET.get('b')
        if buyer:
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                buyer__name__contains=buyer)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                order_date=order_date)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                entry_date=entry_date)

        send_date = self.request.GET.get('sd')
        if send_date:
            send_date = datetime.strptime(send_date, '%Y-%m-%d').date()
            context['missing_data_archives'] = context['missing_data_archives'].filter(
                exit_date=send_date)

        return context


class InputMissingStorage(LoginRequiredMixin, TemplateView):
    template_name = 'base/input_missing_storage.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['missing_data_storage'] = InStorageShoe.objects.filter(
            Q(buy_invoice_nr__exact='') | Q(buy_invoice_date__isnull=True))

        name = self.request.GET.get('n')
        if name:
            context['missing_data_storage'] = context['missing_data_storage'].filter(
                name__contains=name)

        seller = self.request.GET.get('s')
        if seller:
            context['missing_data_storage'] = context['missing_data_storage'].filter(
                seller__name__contains=seller)

        order_date = self.request.GET.get('od')
        if order_date:
            order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
            context['missing_data_storage'] = context['missing_data_storage'].filter(
                order_date=order_date)

        entry_date = self.request.GET.get('ed')
        if entry_date:
            entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            context['missing_data_storage'] = context['missing_data_storage'].filter(
                entry_date=entry_date)

        return context


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
                sold_shoe.email = form.cleaned_data['email']
                sold_shoe.buy_price = form.cleaned_data['buy_price']
                sold_shoe.name = form.cleaned_data['name']
                sold_shoe.size = form.cleaned_data['size']
                sold_shoe.order_date = form.cleaned_data['order_date']
                sold_shoe.seller = form.cleaned_data['seller']
                sold_shoe.comment = form.cleaned_data['comment']

                sold_shoe.entry_date = form.cleaned_data['entry_date']
                sold_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                sold_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']

                sold_shoe.exit_date = form.cleaned_data['exit_date']
                sold_shoe.sell_invoice_nr = form.cleaned_data['sell_invoice_nr']
                sold_shoe.sell_invoice_date = form.cleaned_data['sell_invoice_date']
                sold_shoe.money_income_date = form.cleaned_data['money_income_date']
                sold_shoe.sell_price = form.cleaned_data['sell_price']
                sold_shoe.buyer = form.cleaned_data['buyer']
                sold_shoe.tracking_nr = form.cleaned_data['tracking_nr']
                sold_shoe.stockx_nr = form.cleaned_data['stockx_nr']
                sold_shoe.cw = form.cleaned_data['cw']

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
                in_storage_shoe.email = form.cleaned_data['email']
                in_storage_shoe.buy_price = form.cleaned_data['buy_price']
                in_storage_shoe.name = form.cleaned_data['name']
                in_storage_shoe.size = form.cleaned_data['size']
                in_storage_shoe.order_date = form.cleaned_data['order_date']
                in_storage_shoe.seller = form.cleaned_data['seller']
                in_storage_shoe.comment = form.cleaned_data['comment']

                in_storage_shoe.entry_date = form.cleaned_data['entry_date']
                in_storage_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                in_storage_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']

                in_storage_shoe.save()

                messages.success(
                    request, f'Pomyślnie uzupełniono dane! Numer magazynowy przesyłki to: {in_storage_shoe.id}')
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
                incomming_shoe.email = form.cleaned_data['email']
                incomming_shoe.buy_price = form.cleaned_data['buy_price']
                incomming_shoe.name = form.cleaned_data['name']
                incomming_shoe.size = form.cleaned_data['size']
                incomming_shoe.order_date = form.cleaned_data['order_date']
                incomming_shoe.seller = form.cleaned_data['seller']
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
            return redirect('chceck-incomming')
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
                in_storage_shoe.email = form.cleaned_data['email']
                in_storage_shoe.buy_price = form.cleaned_data['buy_price']
                in_storage_shoe.name = form.cleaned_data['name']
                in_storage_shoe.size = form.cleaned_data['size']
                in_storage_shoe.order_date = form.cleaned_data['order_date']
                in_storage_shoe.seller = form.cleaned_data['seller']
                in_storage_shoe.comment = form.cleaned_data['comment']

                in_storage_shoe.entry_date = form.cleaned_data['entry_date']
                in_storage_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                in_storage_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']

                in_storage_shoe.save()

                messages.success(
                    request, f'Pomyślnie edytowano przesyłkę w magazynie! Numer magazynowy przesyłki to: {in_storage_shoe.id}')
                return redirect('check-storage')

        messages.error(
            request, 'Podczas edytowania przesyłki na magazynie wystąpił błąd!')
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
                sold_shoe.email = form.cleaned_data['email']
                sold_shoe.buy_price = form.cleaned_data['buy_price']
                sold_shoe.name = form.cleaned_data['name']
                sold_shoe.size = form.cleaned_data['size']
                sold_shoe.order_date = form.cleaned_data['order_date']
                sold_shoe.seller = form.cleaned_data['seller']
                sold_shoe.comment = form.cleaned_data['comment']

                sold_shoe.entry_date = form.cleaned_data['entry_date']
                sold_shoe.buy_invoice_nr = form.cleaned_data['buy_invoice_nr']
                sold_shoe.buy_invoice_date = form.cleaned_data['buy_invoice_date']

                sold_shoe.exit_date = form.cleaned_data['exit_date']
                sold_shoe.sell_invoice_nr = form.cleaned_data['sell_invoice_nr']
                sold_shoe.sell_invoice_date = form.cleaned_data['sell_invoice_date']
                sold_shoe.money_income_date = form.cleaned_data['money_income_date']
                sold_shoe.sell_price = form.cleaned_data['sell_price']
                sold_shoe.buyer = form.cleaned_data['buyer']
                sold_shoe.tracking_nr = form.cleaned_data['tracking_nr']
                sold_shoe.stockx_nr = form.cleaned_data['stockx_nr']
                sold_shoe.cw = form.cleaned_data['cw']

                sold_shoe.save()

                messages.success(
                    request, f'Pomyślnie edytowano przesyłkę w archiwum! Numer magazynowy przesyłki to: {sold_shoe.storage_nr}')
                return redirect('archives')

        messages.error(
            request, 'Podczas edytowania przesyłki w archiwum wystąpił błąd!')
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
            order_date__month=month, order_date__year=year)

        archives_this_month = SoldShoe.objects.filter(
            order_date__month=month, order_date__year=year)

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

        context['income'] = income
        context['costs'] = costs
        context['profit'] = 0.97 * float(income) - float(costs)
        context['tax'] = 0.03 * float(income)

        # INCOME COSTS last year
        last_year = dict(zip([f'{date.month}.{date.year}' for date in last_12_months], [
                         {'income': 0, 'costs': 0, 'profit': 0} for _ in range(12)]))

        incomming_last_year = IncommingShoe.objects.filter(
            order_date__gte=year_ago)
        in_storage_last_year = InStorageShoe.objects.filter(
            order_date__gte=year_ago)
        sold_last_year = SoldShoe.objects.filter(
            order_date__gte=year_ago)

        for shoe in list(incomming_last_year) + list(in_storage_last_year) + list(sold_last_year):
            last_year[f'{shoe.order_date.month}.{shoe.order_date.year}']['costs'] += int(
                shoe.buy_price)

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
            order_date__gte=three_months_ago)
        archives_last_3_months = SoldShoe.objects.filter(
            order_date__gte=three_months_ago)

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
