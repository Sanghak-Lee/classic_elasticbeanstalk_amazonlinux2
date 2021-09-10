from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField

#'value(단계)', 'key(보여지는 key)'
ORDERDETAIL_CHOICES = (
    (1, '1단계'), #주문접수
    (2, '2단계'), #영상제작중
    (3, '3단계'), #영상편집중
    (4, '4단계')  #전달완료
)


INSTRUMENT_CHOICES = (
    ('H', '현악기'),
    ('G', '관악기'),
    ('T', '타악기'),
    ('ETC', '기타')
)




CATEGORY_CHOICES = (
    ('H', '현악기'),
    ('G', '관악기'),
    ('T', '타악기'),
    ('ETC', '기타')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'), #speical request
    ('S', 'Shipping'),
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3, default="ETC")
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField()
    image = models.ImageField(upload_to='item/image')
    video = models.FileField(upload_to='item/video')
    slug = models.SlugField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    like_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_item',  blank=True)
    onlyforartist = models.BooleanField(default = False)
    onlyforspecial = models.BooleanField(default=False)
    special_price = models.IntegerField(null=True) #special album 살때 가격
    discount_special_price = models.IntegerField(null=True, blank=True)  # special album 살때 가격
    recommend = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_direct_add_to_cart_url(self):
        return reverse("core:direct_add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    ordered_detail = models.IntegerField(choices=ORDERDETAIL_CHOICES, null= True, blank = True)
    updated = models.DateTimeField(auto_now=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null = True, related_name="orderitem_author")

    def __str__(self):
        return f"{self.quantity} * {self.item.title} orderby:{self.user.username}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def article_upload_time(self):

            for a in self.article_orderitem.all():
                return a.start_date



class Article(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, blank= True, null = True)
    description = models.TextField(blank = True, null = True)
    image = models.ImageField(upload_to='article/image', blank= True, null = True)
    video = models.FileField(upload_to='article/video', blank= True, null = True)
    slug = models.SlugField(null = True, blank = True)
    article_password = models.CharField(max_length=20, null=True, blank = True)
    embedurl = models.CharField(max_length=200)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='client')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='author')
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, related_name='article_orderitem')
    start_date = models.DateTimeField(auto_now_add=True, null = True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:customer_product", kwargs={
            'slug': self.slug
        })

    def password(self):
        return reverse("core:customer_product", kwargs={
            'slug': self.slug
        })



class Video(models.Model):
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/')

    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

        def __str__(self):
            return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profile/image', blank=True)
    video = models.FileField(upload_to='profile/video')
    instrument = models.CharField(choices=INSTRUMENT_CHOICES, max_length=3)
    description = models.CharField(max_length = 100, blank=True, null=True)
    followers = models.ManyToManyField("self", blank=True, related_name="followers")
    followings = models.ManyToManyField("self", blank=True, related_name="followings")
    start_date = models.DateTimeField(auto_now_add=True, null = True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("core:artist_profile_detail", kwargs={
            'pk': self.pk
        })

#MD 추천상품
class BG_MDPICK(models.Model):
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title

class SM_MDPICK(models.Model):
    title = models.CharField(max_length=100)
    items = models.ManyToManyField(Item, blank=True, related_name="md_items")
    artists = models.ManyToManyField(UserProfile,  blank=True, related_name="md_artists")
    bg_mdpick=models.ForeignKey(BG_MDPICK, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField(max_length=50)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True, null=True)




class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    address = models.ForeignKey(
        'Address', related_name='address', on_delete=models.SET_NULL, null=True)
    special_address = models.ForeignKey(
        'Address', related_name='special_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    PG = models.CharField(max_length = 10)
    pre_request = models.CharField(max_length=100, blank=True, null=True)
    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
         return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_count(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total

    def get_item_name(self):
        name = ''
        for order_item in self.items.all():
            name += str(order_item) + ', '
        return name


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    email = models.CharField(max_length=100, null=True)
    request = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, null=True)
    zip = models.CharField(max_length=10, null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.phone)

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.amount)


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance, pk=instance.pk)

post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
