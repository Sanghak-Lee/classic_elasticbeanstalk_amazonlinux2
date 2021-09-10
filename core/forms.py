from django import forms
from django.conf import settings
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Video, Item, Article, Comment, OrderItem
from allauth.account.forms import LoginForm

PAYMENT_CHOICES = (
    ('K', 'Kakao'),
    ('P', 'PayPal'),
    ('T', 'Toss'),
)

class Article_uploadForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['video', 'title', 'description', 'article_password', 'client', 'orderitem']
    def __init__(self, user, *args, **kwargs):
        super(Article_uploadForm, self).__init__(*args, **kwargs)
#user하는 중       self.fields['client'].queryset = settings.AUTH_USER_MODEL.objects.filter(pk=)
        self.fields['orderitem'].queryset = OrderItem.objects.filter(author=user, ordered=True, ordered_detail=1)

class CustomLoginForm(LoginForm):

    def get(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(CustomLoginForm, self).login(*args, **kwargs)

class CommentForm(forms.ModelForm):
    content = forms.CharField(
                label='댓글',
                widget=forms.Textarea(
                        attrs={
                            'rows': 2,
                        }
                    )
            )
    class Meta:
        model = Comment
        fields = ['content']

class LForm(forms.Form):
    password = forms.CharField(required=True)
    username = forms.CharField(required=True)

class passwordForm(forms.Form):
    password = forms.CharField(required=True)

class seller_upload(forms.ModelForm):
    class Meta:
        model = Item
        fields = {'title', 'price', 'discount_price', 'category', 'label', 'description', 'image', 'video', 'slug','special_price','discount_special_price'}


class UploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = {'title', 'video'}


class CheckoutForm(forms.Form):
    email = forms.CharField(required=False)
    request = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    zip = forms.CharField(required=False)

    s_email = forms.CharField(required=False)
    s_request = forms.CharField(required=False)
    s_phone = forms.CharField(required=False)
    s_zip = forms.CharField(required=False)

    same_special_address = forms.BooleanField(required=False)
    set_default_address = forms.BooleanField(required=False)
    use_default_address = forms.BooleanField(required=False)
    set_default_special_address = forms.BooleanField(required=False)
    use_default_special_address = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '쿠폰입력',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
