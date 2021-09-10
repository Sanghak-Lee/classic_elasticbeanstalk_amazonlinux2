from django import template
from core.models import Order, UserProfile, Item

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0

@register.filter
def following_count(user):
    if user.is_authenticated:
        userprofile = UserProfile.objects.filter(user=user)
        if userprofile.exists():
            return userprofile[0].followings.count()
    return 0

@register.filter
def follower_count(user):
    if user.is_authenticated:
        userprofile = user.userprofile
        if userprofile.exists():
            return userprofile.followers.count()
    return 0

@register.filter
def like_count(user):
    if user.is_authenticated:
        item = user.like_item.all()
        if item.exists():
            return item.count()
    return 0

@register.simple_tag(takes_context=True)
def get_order_list(context):
    request = context['request']
    return Order.objects.filter(user=request.user, ordered=False)