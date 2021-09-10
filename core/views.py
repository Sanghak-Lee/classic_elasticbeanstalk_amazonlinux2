import random
import string
import json, os, vimeo
from parse import *
import urllib.request
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, UploadForm, seller_upload, CommentForm, passwordForm, CustomLoginForm, LForm, Article_uploadForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Video, Article, SM_MDPICK, BG_MDPICK
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from invitations.utils import get_invitation_model
import requests
VIMEO_SECRET_KEY = settings.VIMEO_SECRET_KEY

#중복으로 보내기전에 filter 하는 기능 추가
#signup완료됐을때 inviter을 검색해서 reward 넣기기능
#publish했을때 packages 수정본도 같이 보내지는지 확인

@login_required
def send_invitation(request):
    Invitation = get_invitation_model()
    invite = Invitation.create('eaa0305@naver.com', inviter=request.user)
    invite.send_invitation(request)
    messages.success(request, "특별 초대장을 전송했습니다. 초대링크는 단 3일간 유효합니다")
    return redirect('core:home')

def begin(request):
    items = Item.objects.all()
    userprofiles = UserProfile.objects.all()
    return render(request, "begin.html", {"items":items, "userprofiles":userprofiles})

def introduce(request):
    return render(request, "introduce.html", None)

class article_upload(View):

    def get(self, request, *args, **kwargs):
        order_list = Order.objects.filter(user=request.user, ordered=False)
        form = Article_uploadForm()
        context = {
            'order_list': order_list,
            'form': form
        }

        return render(request, 'account/myvideopage.html', context)

    def post(self ,request, *args, **kwargs):
        order_list = Order.objects.filter(user=request.user, ordered=False)
        form = Article_uploadForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            v = vimeo.VimeoClient(
                token = 'f2e8eaa7fe9fcf4358433f77e369770d',
                key = '6bd32199cdfca969f81ea9b636fd4182dc49228b',
                secret = VIMEO_SECRET_KEY
            )
            file_data = request.FILES["file_data"]
            path = file_data.temporary_file_path()
            try:
                vimeo_authorization_url = v.auth_url(
                    ['private'],
                    'http://127.0.0.1:8000/',
                    1
                )
                name = form.author.username + "→" + form.client.username
                description = "password : " + form.article_password + "\n" + "Title : " + form.title + "\n" + form.description
                video_uri = v.upload(path, data={'name': name, 'description': description})
                v.patch(video_uri, data={'privacy': {'view': 'password', 'download': False}, 'password': form.article_password})
                video_data = v.get(video_uri + '?fields=link').json()
                video_url = video_data['link']
                video_id = parse("https://vimeo.com/{id}", video_url)

                #            headers = {'Content-Type': 'application/json; charset=utf-8'}
                #            content1 = requests.get('https://vimeo.com/api/oembed.json', params=params1, headers=headers)
                #            print('"{}" has been uploaded to {}'.format(file_data, video_data['link']))

                embedurl = "<div style = 'padding:56.34% 0 0 0;position:relative;'><iframe src = 'https://player.vimeo.com/video/{0}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479' frameborder = '0' allow = 'autoplay; fullscreen; picture-in-picture' allowfullscreen style = 'position:absolute;top:0;left:0;width:100%;height:100%;' title={1}></iframe></div><script src = 'https://player.vimeo.com/api/player.js'></script>".format(video_id["id"], form.title)
                form.title = name
                form.description=description
                form.embedurl = embedurl

                #제작중으로 승급
                orderitem = form.orderitem
                orderitem.ordered_detail = 2
                orderitem.save()
                # 결제 -> 판매자창 -> 비디오 업로드 -> 주문자창 자동화 FLOW 작업중
                # client_order = Order.Objects.filter(user=form_article.client)
                # for a in client_order:

                #video 모델 article 저장!
                form.save()
                context = {
                    'order_list': order_list,
                }
                messages.success(request, "비디오 업로드가 완료되었습니다. 팬분께 비디오를 전달해드릴게요!")
                return render(request, 'account/mypage.html', context)

            except vimeo.exceptions.VideoUploadFailure as e:
                messages.info(request, "업로드에 실패하였습니다.")

            finally:
                file_data.close()  # Theoretically this should remove the file
                if os.path.exists(path):
                    os.unlink(path)  # But this will do it, barring permissions

        messages.info(request, "업로드에 문제가 생겼습니다.")
        return render(request, 'account/mypage.html', None)





def myvideopage(request, pk):
    user = get_object_or_404(User, pk=pk)
    order = Order.objects.filter(user=request.user, ordered=True)
    article = Article.objects.filter(client=request.user)

    context = {
        'user': user,
        'order': order,
        'article':article
    }
    if request.method == 'POST':

        form = seller_upload(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()

        return render(request, 'account/myvideopage.html', context)
    else:
        form = seller_upload()
       # order = Order.objects.filter(user=request.user, ordered=True)
        context = {
            'user': user,
            'form': form,
            'order': order,
            'article' : article
        }
        return render(request, 'account/myvideopage.html', context)


    #return render(request, 'account/mypage.html', context)


def payment_complete(request):
    messages.success(request, "Your order was successful!")
    qs = Order.objects.filter(user=request.user, ordered=True).order_by('-ordered_date')
    order_complete = qs[0]
    context={
        'order': order_complete
    }
    return render(request, "payment_complete.html", context)

def special_product(request, pk, orderitem_pk):
    user = get_object_or_404(User, pk=pk)
    orderitem = get_object_or_404(OrderItem, pk=orderitem_pk, user=user)
    return redirect("core:product", slug=orderitem.item.slug)

@login_required
def like_album(request, pk):
    like_item = request.user.like_item.all()
    if like_item.exists():
        context={
            'like_item':like_item
        }
        return render(request, 'account/like_album.html', context)
    else:
        messages.info(request, "좋아하는 상품이 없습니다. 이제부터 좋아해 보시는건 어떨까요?")
        return redirect('core:product_list')

@login_required
def like_artist(request, pk):
    like_artist=request.user.userprofile.followings.all()
    if like_artist.exists():
        context={
            'like_artist':like_artist
        }
        return render(request, 'account/like_artist.html', context)

    else:
        messages.info(request, "좋아하는 아티스트가 없습니다. 이제부터 좋아해 보시는건 어떨까요?")
        return redirect('core:artist_profile')

@login_required
def specialalbum_add_to_cart(request, pk, orderitem_pk):

    orderitem=get_object_or_404(OrderItem, pk=orderitem_pk, user= request.user)
    orderitem.author=orderitem.item.user
    item, created = Item.objects.get_or_create(
        title = orderitem.item.title + "의 스페셜 에디션",
        description = orderitem.item.title + "\n" + orderitem.item.user.username + "아티스트님이 특별한 추억을 실물로 만들어 보내드릴게요!",
        slug = orderitem.item.slug + "special",
        onlyforspecial=True,
        user=orderitem.item.user,
        price=orderitem.item.special_price,
        discount_price = orderitem.item.discount_special_price,
        image = orderitem.item.image,
        video = orderitem.item.video
    )
    item.price = orderitem.item.special_price
    item.discount_price = orderitem.item.discount_special_price


    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        author=item.user
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order.pre_request = orderitem.item.user.username + "아티스트님의 Speical Edition 주문 중입니다."
        order.save()
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:checkout")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:checkout")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.pre_request = orderitem.item.user.username + "아티스트님의 Speical Edition 주문 중입니다."
        order.save()
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:checkout")


    return redirect("/")




def myorder(request, pk):
    user = get_object_or_404(User, pk=pk)
    order = Order.objects.filter(user=request.user, ordered=True)
    order_list = Order.objects.filter(user=request.user, ordered=False)
    context = {
        'user': user,
        'order': order,
        'order_list' : order_list
    }
    return render(request, 'account/myorder.html', context)


def mypage(request, pk):
    user = get_object_or_404(User, pk=pk)
    order = Order.objects.filter(user=request.user, ordered=True)
    order_list = Order.objects.filter(user=request.user, ordered=False)
    context = {
        'user': user,
        'order': order,
        'order_list' : order_list
    }
    if request.method == 'POST':

        form = Article_uploadForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()

        return render(request, 'account/mypage.html', None)
    else:
        form = Article_uploadForm(user)
       # order = Order.objects.filter(user=request.user, ordered=True)
        context = {
            'user': user,
            'form': form,
            'order': order,
            'order_list':order_list
        }
        return render(request, 'account/mypage.html', context)


    #return render(request, 'account/mypage.html', context)

def aran(request):
    return render(request, "aran/aran.html", None)


def video_new(request):
    if request.method == 'POST':
        #title = request.POST['title']
        #video = request.POST['video']

        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect("core:video_list")
    else:
        form = UploadForm()
        return render(request, 'videos/video_new.html', {'form': form})


#하드코딩... 실험적으로 해보고 request.GET.get('next','') 으로 httpresponseredirect 해서 뒤로가기해라...
@login_required()
def like_item(request, pk, select):
#    if request.method == 'POST':
        item = get_object_or_404(Item, pk=pk)
        if request.user in item.like_user.all():
            item.like_user.remove(request.user)
            if(select==1):
                return redirect("core:product_list")
            elif(select==2):
                return redirect("core:product", item.slug)
            else:
                return redirect("core:home")
        else:
            item.like_user.add(request.user)
            if(select==1):
                return redirect("core:product_list")
            elif(select==2):
                return redirect("core:product", item.slug)
            else:
                return redirect("core:home")

@login_required()
def follow_userprofile(request, pk):
        next = request.GET.get('next','/')
        target_userprofile = get_object_or_404(UserProfile, pk=pk)

        # 언팔
        if request.user.userprofile in target_userprofile.followers.all():
            target_userprofile.followers.remove(request.user.userprofile)
            request.user.userprofile.followings.remove(target_userprofile)

        # 팔로우
        else:
            target_userprofile.followers.add(request.user.userprofile)
            request.user.userprofile.followings.add(target_userprofile)

        return HttpResponseRedirect(next)

@login_required()
def product_review(request, pk):
#    if request.method == 'POST':
        item = get_object_or_404(Item, pk=pk)
        comment = CommentForm(request.POST)
        if comment.is_valid():
            comment = comment.save(commit=False)
            comment.user = request.user
            comment.item = item
            comment.save()
        return redirect("core:product", item.slug)


def video_list(request):
    video_list = Video.objects.all()
    return render(request, 'videos/video.html', {'video_list': video_list})

def seller_item_new(request):
    if request.method == 'POST':
        title = request.POST['title']
        text = request.POST['text']
        image = request.POST['image']
        video = request.POST['video']
        form = seller_upload(request.POST, request.FILES)
        if form.is_valid():
            form.user=request.user
            form.save()
            return redirect("core:mypage")
    else:
        form = seller_upload()
        return render(request, 'mypage/mypage_upload.html', {'form':form})

def seller_item_list(request):
    context = {
        'title' : Article.title.object.all(),
        'text': Article.text.object.all(),
        'video': Article.video.object.all(),
        'image': Article.image.object.all()
    }

    return render(request, 'mypage.html', {'seller_item_list': context})




def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if address_qs.exists():
                context.update(
                    {'default_address': address_qs[0]})

            special_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if special_address_qs.exists():
                context.update(
                    {'default_special_address': special_address_qs[0]})
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:home")



    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_address = form.cleaned_data.get(
                    'use_default_address')
                if use_default_address:
                    print("Using the default request")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        address = address_qs[0]
                        order.address = address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default request available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new request")
                    email = form.cleaned_data.get(
                        'email')
                    request = form.cleaned_data.get(
                        'request')
                    phone = form.cleaned_data.get(
                        'phone')
                    zip = form.cleaned_data.get('zip')

                    if is_valid_form([email, request, phone, zip]):
                        address = Address(
                            user=self.request.user,
                            email=email,
                            request=request,
                            phone=phone,
                            zip=zip,
                            address_type='S'
                        )
                        address.save()

                        order.address = address
                        order.save()

                        set_default_address = form.cleaned_data.get(
                            'set_default_address')
                        if set_default_address:
                            address.default = True
                            address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required request fields")
                        return redirect('core:checkout')

                use_default_special_address = form.cleaned_data.get(
                    'use_default_special_address')
                same_special_address = form.cleaned_data.get(
                    'same_special_address')

                if same_special_address:
                    # special_address = address
                    # special_address.pk = None
                    # special_address.save()
                    # special_address.address_type = 'B'
                    # special_address.save()
                    # order.special_address = special_address
                    # order.save()
                    order.special_address = None
                    order.save()

                elif use_default_special_address:
                    print("Using the default special request")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        special_address = address_qs[0]
                        order.special_address = special_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default special request available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new special request")
                    s_email = form.cleaned_data.get(
                        's_email')
                    s_request = form.cleaned_data.get(
                        's_request')
                    s_phone = form.cleaned_data.get(
                        's_phone')
                    s_zip = form.cleaned_data.get('s_zip')

                    if is_valid_form([s_email, s_phone, s_zip, s_request]):
                        special_address = Address(
                            user=self.request.user,
                            email=s_email,
                            request=s_request,
                            phone=s_phone,
                            zip=s_zip,
                            address_type='B'
                        )
                        special_address.save()

                        order.special_address = special_address
                        order.save()

                        set_default_special_address = form.cleaned_data.get(
                            'set_default_special_address')
                        if set_default_special_address:
                            special_address.default = True
                            special_address.save()




                    else:
                        messages.info(
                            self.request, "특별요청 사항 없음 버튼을 눌러주세요")
                        return redirect('core:checkout')

                payment_option = form.cleaned_data.get('payment_option')
                order.PG = payment_option
                order.save()
                if payment_option == 'T':
                    return redirect('core:payment', payment_option='toss')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                elif payment_option == 'K':
                    return redirect('core:payment', payment_option='kakao')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            else:
                messages.warning(
                    self.request, "적절하지 않은 형식입니다. 형식을 맞춰서 기입해주세요")
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")



class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        # if order.special_address:
        context = {
            'order': order,
            'DISPLAY_COUPON_FORM': False
           # 'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
        }
        userprofile = self.request.user.userprofile
        # if userprofile.one_click_purchasing:
        #     # fetch the users card list
        #     cards = stripe.Customer.list_sources(
        #         userprofile.stripe_customer_id,
        #         limit=3,
        #         object='card'
        #     )
        #     card_list = cards['data']
        #     if len(card_list) > 0:
        #         # update the context with the default card
        #         context.update({
        #             'card': card_list[0]
        #         })
        return render(self.request, "payment.html", context)
        # else:
        #     messages.warning(
        #         self.request, "You have not added a billing address")
        #     return redirect("core:checkout")


    def post(self, request, *args, **kwargs):
        data = request.body
        data = data.decode('utf-8')

        if data[8] == "t":

            order = Order.objects.get(user=self.request.user, ordered=False)
            #form = PaymentForm(self.request.POST)
            userprofile = UserProfile.objects.get(user=self.request.user)
            #if form.is_valid():
            #token = form.cleaned_data.get('stripeToken')
            #save = form.cleaned_data.get('save')
            #use_default = form.cleaned_data.get('use_default')

            # if save:
            #     if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            #         customer = stripe.Customer.retrieve(
            #             userprofile.stripe_customer_id)
            #         customer.sources.create(source=token)
            #
            #     else:
            #         customer = stripe.Customer.create(
            #             email=self.request.user.email,
            #         )
            #         customer.sources.create(source=token)
            #         userprofile.stripe_customer_id = customer['id']
            #         userprofile.one_click_purchasing = True
            #         userprofile.save()





                # if use_default or save:
                #     # charge the customer because we cannot charge the token more than once
                #     charge = stripe.Charge.create(
                #         amount=amount,  # cents
                #         currency="usd",
                #         customer=userprofile.stripe_customer_id
                #     )
                # else:
                #     # charge once off on the token
                #     charge = stripe.Charge.create(
                #         amount=amount,  # cents
                #         currency="usd",
                #         source=token
                #     )

            # create the payment



            payment = Payment()
            #payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True, ordered_detail=1)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.user = self.request.user
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")

            return render(self.request, "payment_complete.html", {'order' : order})

        else:
            messages.warning(
                self.request, "결제가 처리되지 않았습니다. 다시한번 확인해주세요")
            return redirect("core:checkout")

class Artist_HomeView(ListView):
    model = Item
    paginate_by = 20
    template_name = "artist_home.html"
    # def get_context_data(self, **kwargs):
    #     context = super(Artist_HomeView, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context

class HomeView(ListView):

    model = Item
    paginate_by = 8
    template_name = "home.html"
    form_class = LForm

    # def get_context_data(self, **kwargs):
    #     context = super(HomeView, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context

class artist_profile(ListView):

    model = UserProfile
    paginate_by = 8
    template_name = "artist_profile/artist_profile.html"

    # def get_context_data(self, **kwargs):
    #     context = super(artist_profile, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #
    #     return context


class MD_artist_profile(ListView):
    mdpick = ""
    def get(self, request, *args, **kwargs):
        self.mdpick = request.GET.get('mdpick')
        return super(MD_artist_profile, self).get(request, *args, **kwargs)

    model = UserProfile
    paginate_by = 8
    template_name = "artist_profile/artist_profile.html"

    #    User = get_user_model()
    def get_context_data(self, **kwargs):
        context = super(MD_artist_profile, self).get_context_data(**kwargs)
        sm_mdpick = get_object_or_404(SM_MDPICK, title=self.mdpick)
        context['mdpick'] = self.mdpick
        context['object_list'] = sm_mdpick.artists.all()
        return context


def artist_profile_detail(request, pk):
    userprofile = get_object_or_404(UserProfile, pk=pk)
    context = {
        'userprofile': userprofile
    }
    return render(request, 'artist_profile/artist_profile_detail.html', context)


class myvideolist(ListView):
    model = Article
    paginate_by = 8
    template_name = "myvideolist.html"

    # def get_context_data(self, **kwargs):
    #     context = super(myvideolist, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class ItemListView(ListView):

    model = Item
    paginate_by = 8
    template_name = "product_list.html"
    User = get_user_model()
    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
        context['artist_list'] = User.objects.filter(is_staff=True)
        return context

class MD_ItemListView(ListView):
    mdpick=""
    def get(self, request, *args, **kwargs):
        self.mdpick=request.GET.get('mdpick')
        return super(MD_ItemListView, self).get(request, *args, **kwargs)

    model = Item
    paginate_by = 8
    template_name = "product_list.html"
    User = get_user_model()
    def get_context_data(self, **kwargs):
        context = super(MD_ItemListView, self).get_context_data(**kwargs)
        sm_mdpick = get_object_or_404(SM_MDPICK, title=self.mdpick)
        context['artist_list'] = User.objects.filter(is_staff=True)
        context['mdpick'] = self.mdpick
        context['object_list'] = sm_mdpick.items.all()
        return context

class ItemDetailView(FormMixin,DetailView):
    form_class = CommentForm
    model = Item
    template_name = "product.html"
    # def get_context_data(self, **kwargs):
    #     context = super(ItemDetailView, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context

class customer_ItemDetailView(FormMixin,DetailView):

    form_class = passwordForm
    model = Article
    template_name = "customer_password.html"
    def post(self, request, *args, **kwargs ):
        this_slug = get_object_or_404(Article, slug=self.kwargs['slug'])
        form_class = passwordForm(request.POST)
        if form_class.is_valid():
            password = form_class.cleaned_data.get('password')
            print(password)
            model = Article.objects.filter(slug=this_slug)
            model = model[0]
            print(model)
            if model.article_password == password:
                return render(self.request, "customer_product.html", {'object': model} )
            else:
                messages.info(request, "비밀번호가 잘못되었습니다")
                return redirect("core:myvideolist")
        else :
            messages.info(request, "입력이 잘못되었습니다")
            return redirect("core:myvideolist")
    # def get_context_data(self, **kwargs):
    #     context = super(customer_ItemDetailView, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context


class Artist_ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    # def get_context_data(self, **kwargs):
    #     context = super(HomeView, self).get_context_data(**kwargs)
    #     if self.request.user.is_authenticated:
    #         context['order_list'] = Order.objects.filter(user=self.request.user, ordered=False)
    #     return context


@login_required
def direct_add_to_cart(request, slug):
#    direct_message = CommentForm(request.POST)
#    if direct_message.is_valid():
#        content = direct_message.cleaned_data['content']
#        item = get_object_or_404(Item, slug=slug)
#        order_item, created = OrderItem.objects.get_or_create(
#            item=item,
#            user=request.user,
#            ordered=False
#        )
    if request.method == 'POST':
        content = request.POST.get('pre_request')
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False,
            author=item.user
        )


        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order.pre_request = content
            order.save()
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:checkout")
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                return redirect("core:checkout")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.pre_request = content
            order.save()
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:checkout")


    return redirect("core:product")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        author=item.user
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
                author=item.user
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False,
        author=item.user
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")




# def page_not_found(request,exception):
#     response = render_to_response('error/404.html')
#     response.status_code = 404
#     return response

def page_not_found(request):
    return render(request, 'error/404.html', None)

def server_error(request):
    return render(request, 'error/500.html', status=500)