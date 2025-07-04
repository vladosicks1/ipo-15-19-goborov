from django.contrib import admin
from .models import PROIZVOD, KATEGOR_TOVAR, TOVAR, User, BASKET, ELEMENT_BASKET

class TOVARAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'proizvod')
    list_filter = ('category', 'proizvod')
    search_fields = ('name',)

class BASKET_ITEMInline(admin.TabularInline):
    model = ELEMENT_BASKET
    extra = 1

class BASKETAdmin(admin.ModelAdmin):
    inlines = [BASKET_ITEMInline]

admin.site.register(PROIZVOD)
admin.site.register(KATEGOR_TOVAR)
admin.site.register(TOVAR, TOVARAdmin)
admin.site.register(BASKET, BASKETAdmin)