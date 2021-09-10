from django.urls import path
from .views import (
    begin,
    HomeView,
    introduce,
    #쿠폰
    AddCouponView,

    #장바구니,Ordersummary
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,

    #환불, 결제
    CheckoutView,
    payment_complete,
    PaymentView,
    RequestRefundView,

    #15초 게시판
    video_list,
    video_new,

    #마이페이지
    mypage,
    myvideopage, #마이페이지+내가구매한영상

    article_upload,

    #비디오 찾으러 가는 게시판
    myvideolist,
    customer_ItemDetailView,

    # 아티스트 페이지
    aran,  #아티스트 특별 프로필 페이지
    Artist_HomeView, #아티스트에게 판매하는 상품 진열 home
    Artist_ItemDetailView, #아티스트에게 판매하는 제품 디테일
    artist_profile,
    artist_profile_detail,

    #팔로우,언팔
    follow_userprofile,

    #좋아요
    like_album,
    like_artist,

    #Item
    ItemListView,
    ItemDetailView,
    direct_add_to_cart,
    product_review,
    like_item,

    # MDPICK
    MD_ItemListView,
    MD_artist_profile,

    #order
    specialalbum_add_to_cart, #item create or get함
    special_product, #그 상품으로만 돌아감
    myorder,

    #for fun
    page_not_found,
    send_invitation

#    seller_item_new,
#    seller_item_list
)

app_name = 'core'

urlpatterns = [
    path('invite/', send_invitation, name='invitation'),
    path('begin/', begin, name='begin'),
    path('', HomeView.as_view(), name='home'),
    path('introduce/', introduce, name='introduce'),
    path('404/', page_not_found , name='404'),

    #MD PICK
    path('MDPICK_ITEM/', MD_ItemListView.as_view(), name='MDPICK_ITEM'),
    path('MDPICK_ARTIST/', MD_artist_profile.as_view(), name='MDPICK_ARTIST'),  # 아티스트 모아보기

    #ITEM 상세페이지
    path('product_list', ItemListView.as_view(), name='product_list'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('product/review/<int:pk>/', product_review, name='product_review'),
    path('product/like/<int:pk>/<int:select>/', like_item, name='like_item'),


    #장바구니
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('direct_add-to-cart/<slug>/', direct_add_to_cart, name='direct_add-to-cart'),
    path('specialalbum_direct_add-to-cart/<int:pk>/<int:orderitem_pk>/', specialalbum_add_to_cart, name='specialalbum_direct_add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),

    #checkout, 결제, 환불요청
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('payment/complete', payment_complete, name='payment_complete'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    #15초 게시판
    path('video/', video_list, name='video_list'),
    path('video/video_new/', video_new, name='video_new'),

    #아티스트
    path('aran/', aran, name='aran'), #아티스트 특별 프로필 페이지
    path('artist_profile/', artist_profile.as_view(), name='artist_profile'),  # 아티스트 모아보기
    path('artist_profile_detail/<int:pk>/', artist_profile_detail, name='artist_profile_detail'),  # 아티스트 프로필 상세페이지

    #마이페이지
    path('mypage/<int:pk>/', mypage, name='mypage'),
    path('myvideopage/<int:pk>/', myvideopage, name='myvideopage'), #마이페이지 + 비디오리스트

    #비디오 게시판(vimeo 대체 채널)
    path('myvideolist/', myvideolist.as_view(), name='myvideolist'), #비디오 찾으러 가는 게시판
    path('customer_product/<slug>/', customer_ItemDetailView.as_view(), name='customer_product'), #비디오 상세페이지

    #아티스트 메뉴
    path('artist_home/<slug>/', Artist_ItemDetailView.as_view(), name='artist_home'),
    path('artist_home/', Artist_HomeView.as_view(), name='artist_home'), #아티스트 상점
    path('article_upload/<int:pk>/', article_upload.as_view(), name='article_upload'), #팬에게 영상 업로드

    #팔로우,언팔
    path('follow_unfollow/<int:pk>/', follow_userprofile, name='follow_userprofile'),

    #좋아요 페이지
    path('like_album/<int:pk>/', like_album, name='like_album'),
    path('like_artist/<int:pk>/', like_artist, name='like_artist'),

    #order
    path('myorder/<int:pk>/', myorder, name='myorder'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('special_product/<int:pk>/<int:orderitem_pk>/', special_product, name='special_product')


#    path('mypage/<int:pk>/seller_item_new/', mypage, name='seller_item_new'),
#    path('mypage/<int:pk>/seller_item_list/', mypage, name='seller_item_list')
]

