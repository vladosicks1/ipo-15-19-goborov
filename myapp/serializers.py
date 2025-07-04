from rest_framework import serializers
from .models import TOVAR, KATEGOR_TOVAR, PROIZVOD, BASKET, ELEMENT_BASKET

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOVAR
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KATEGOR_TOVAR
        fields = '__all__'

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PROIZVOD
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELEMENT_BASKET
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BASKET
        fields = '__all__'
