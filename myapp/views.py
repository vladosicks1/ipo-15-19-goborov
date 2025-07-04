from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import TOVAR, KATEGOR_TOVAR, PROIZVOD, BASKET, ELEMENT_BASKET
import os, json
from django.core.mail import EmailMessage
from django.http import HttpResponse
from io import BytesIO
from rest_framework import viewsets
from .models import TOVAR, KATEGOR_TOVAR, PROIZVOD, BASKET, ELEMENT_BASKET
from .serializers import ProductSerializer, CategorySerializer, ManufacturerSerializer, CartSerializer, CartItemSerializer


# Главная страница
def main_page(request):
    return render(request, 'main_page.html')


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# О проекте и об авторе
def about_me(request):
    return render(request, 'about_me.html')

def about_project(request):
    return render(request, 'about_project.html')


# Вывод всех квалификаций
def spec(request):
    filepath = os.path.join(os.path.dirname(__file__), 'qualifications.json')
    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return render(request, 'spec.html', {'error': 'Файл не найден'})

    qualifications = []
    for el in data:
        fields = el.get("fields", {})
        qualifications.append({
            'title': fields.get("title", "—"),
            'description': fields.get("description", "—"),
            'code': fields.get("code", "—")
        })

    context = {'qualifications': qualifications, 'count': len(qualifications)}
    return render(request, 'spec.html', context)


# Квалификация по ID
def spec_id(request, id):
    filepath = os.path.join(os.path.dirname(__file__), 'qualifications.json')
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return render(request, 'spec_id.html', {'error': 'Файл квалификаций не найден 😢'})

    for item in data:
        if str(item.get("pk")) == str(id):
            fields = item.get("fields", {})
            raw = fields.get("object_repr", "")
            number, title = "—", "—"
            if "//" in raw:
                parts = raw.split("//")
                number = parts[0].strip()
                title = parts[1].strip()
            return render(request, 'spec_id.html', {
                'number': number,
                'title': title,
                'pk': id
            })

    return render(request, 'spec_id.html', {'error': f'Квалификация с ID {id} не найдена 🚫'})


# Каталог товаров с фильтрами и поиском
def product_list(request):
    products = TOVAR.objects.all()
    categories = KATEGOR_TOVAR.objects.all()
    manufacturers = PROIZVOD.objects.all()

    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    query = request.GET.get('q')

    if category_id:
        products = products.filter(category_id=category_id)
    if manufacturer_id:
        products = products.filter(proizvod_id=manufacturer_id)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'selected_category': category_id,
        'selected_manufacturer': manufacturer_id,
        'search_query': query,
    }
    return render(request, 'product_list.html', context)


# Детальная страница товара
def product_detail(request, pk):
    product = get_object_or_404(TOVAR, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# Добавление товара в корзину
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(TOVAR, pk=product_id)
    basket, _ = BASKET.objects.get_or_create(user=request.user)

    item, created = ELEMENT_BASKET.objects.get_or_create(
        basket=basket,
        tovar=product,
        defaults={'kolvo': 1}
    )

    if not created and item.kolvo < product.kolvo:
        item.kolvo += 1
        item.save()

    return redirect('cart_view')


# Обновление количества в корзине
@login_required
def update_cart(request, item_id):
    item = get_object_or_404(ELEMENT_BASKET, pk=item_id, basket__user=request.user)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if 0 < quantity <= item.tovar.kolvo:
        item.kolvo = quantity
        item.save()

    return redirect('cart_view')


# Удаление товара из корзины
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(ELEMENT_BASKET, pk=item_id, basket__user=request.user)
    item.delete()
    return redirect('cart_view')


# Просмотр корзины
@login_required
def cart_view(request):
    basket, _ = BASKET.objects.get_or_create(user=request.user)
    items = ELEMENT_BASKET.objects.filter(basket=basket).select_related('tovar')
    total = sum(item.item_price() for item in items)
    return render(request, 'cart.html', {'cart_items': items, 'total': total})

@login_required
def checkout_view(request):
    try:
        basket = BASKET.objects.get(user=request.user)
        items = ELEMENT_BASKET.objects.filter(basket=basket)
    except BASKET.DoesNotExist:
        return HttpResponse("Ваша корзина пуста.")

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        if not address:
            return render(request, "shop/checkout.html", {
                "error": "Пожалуйста, укажите адрес доставки.",
                "basket": basket,
                "items": items
            })

        # Генерация текстового чека
        total_sum = basket.total_price()
        lines = [
            f"Чек заказа для пользователя {request.user.username}",
            f"Адрес доставки: {address}",
            "",
            "Список товаров:"
        ]
        for item in items:
            line = f"{item.tovar.name} — {item.kolvo} шт. × {item.tovar.price} руб. = {item.item_price()} руб."
            lines.append(line)

        lines.append("")
        lines.append(f"Итоговая сумма: {total_sum} руб.")

        file_stream = BytesIO()
        file_stream.write("\n".join(lines).encode("utf-8"))
        file_stream.seek(0)

        # Отправка письма с вложением
        email = EmailMessage(
            subject="Ваш заказ успешно оформлен",
            body=f"Спасибо за заказ, {request.user.username}!\nЧек прилагается.",
            from_email="yourshop@example.com",
            to=[request.user.email],
        )
        email.attach("chek.txt", file_stream.read(), "text/plain")
        email.send()

        # Очистка корзины
        items.delete()
        basket.delete()

        return render(request, "shop/checkout_success.html")

    return render(request, "shop/checkout.html", {
        "basket": basket,
        "items": items
    })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = TOVAR.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = KATEGOR_TOVAR.objects.all()
    serializer_class = CategorySerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = PROIZVOD.objects.all()
    serializer_class = ManufacturerSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = BASKET.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = ELEMENT_BASKET.objects.all()
    serializer_class = CartItemSerializer
