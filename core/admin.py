from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, Video, Article, Comment, BG_MDPICK, SM_MDPICK

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'ordered_detail',
                    'author',
                    'updated',
                    'item'
                    ]
    list_display_links = [
      'user',
      'item',
      'author'
    ]
    list_filter = ['ordered_detail',
                   'ordered',
                   'item',
                   'updated',
                   'author',
                   'user'
                   ]
    search_fields = [
        'user',
        'author',
        'item',
    ]

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title',
                    'category',
                    'description',
                    'article_password',
                    'client',
                    'author',
                    'orderitem',
                    'start_date'
                    ]
    list_display_links = [
        'orderitem',
        'clinet',
        'author'
    ]
    list_filter = ['client',
                   'author',
                   'orderitem',
                   'start_date'
                   ]
    search_fields = [
        'client',
        'author',
        'orderitem',
        'start_date'
    ]

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'address',
                    'special_address',
                    'payment',
                    'PG',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'address',
        'special_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email',
        'request',
        'phone',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'phone']
    search_fields = ['user', 'email', 'request', 'zip']


admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Video)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(BG_MDPICK)
admin.site.register(SM_MDPICK)