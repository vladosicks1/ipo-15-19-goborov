from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
class KATEGOR_TOVAR(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

class PROIZVOD(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    country = models.CharField(max_length=100, verbose_name="Страна")
    description = models.TextField(null=True, blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

class TOVAR(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    photo = models.ImageField(upload_to='products/', verbose_name="Фото товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    kolvo = models.IntegerField(verbose_name="Количество на складе")
    category = models.ForeignKey(
        KATEGOR_TOVAR, 
        on_delete=models.CASCADE, 
        verbose_name="Категория"
    )
    proizvod = models.ForeignKey(
        PROIZVOD,
        on_delete=models.CASCADE,
        verbose_name="Производитель"
    )
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной'})
        if self.kolvo < 0:
            raise ValidationError({'kolvo': 'Количество не может быть отрицательным'})
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
class BASKET(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,verbose_name="Пользователь",)
    date = models.DateTimeField(auto_now_add=True,verbose_name="Дата создания")
    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def total_price(self):
        return sum(item.item_price() for item in self.cart_items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
class ELEMENT_BASKET(models.Model):
    basket = models.ForeignKey(BASKET,on_delete=models.CASCADE,verbose_name="Корзина")
    tovar = models.ForeignKey(TOVAR,on_delete=models.CASCADE,verbose_name="Товар")
    kolvo = models.PositiveIntegerField(verbose_name="Количество")
    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    def item_price(self):
        return self.tovar.price * self.kolvo

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"