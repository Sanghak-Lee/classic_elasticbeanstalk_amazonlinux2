# Generated by Django 2.2.14 on 2021-08-26 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, null=True)),
                ('request', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(max_length=15, null=True)),
                ('zip', models.CharField(max_length=10, null=True)),
                ('address_type', models.CharField(choices=[('B', 'Billing'), ('S', 'Shipping')], max_length=1)),
                ('default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='BG_MDPICK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('amount', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
                ('discount_price', models.IntegerField(blank=True, null=True)),
                ('category', models.CharField(choices=[('H', '현악기'), ('G', '관악기'), ('T', '타악기'), ('ETC', '기타')], default='ETC', max_length=3)),
                ('label', models.CharField(choices=[('P', 'primary'), ('S', 'secondary'), ('D', 'danger')], max_length=1)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='item/image')),
                ('video', models.FileField(upload_to='item/video')),
                ('slug', models.SlugField()),
                ('onlyforartist', models.BooleanField(default=False)),
                ('onlyforspecial', models.BooleanField(default=False)),
                ('special_price', models.IntegerField(null=True)),
                ('discount_special_price', models.IntegerField(blank=True, null=True)),
                ('recommend', models.CharField(blank=True, max_length=10, null=True)),
                ('like_user', models.ManyToManyField(blank=True, related_name='like_item', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ref_code', models.CharField(max_length=20)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('ordered_date', models.DateTimeField()),
                ('ordered', models.BooleanField(default=False)),
                ('being_delivered', models.BooleanField(default=False)),
                ('received', models.BooleanField(default=False)),
                ('refund_requested', models.BooleanField(default=False)),
                ('refund_granted', models.BooleanField(default=False)),
                ('PG', models.CharField(max_length=10)),
                ('pre_request', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='address', to='core.Address')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Coupon')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('video', models.FileField(upload_to='videos/')),
            ],
            options={
                'verbose_name': 'video',
                'verbose_name_plural': 'videos',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=50, null=True)),
                ('one_click_purchasing', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, upload_to='profile/image')),
                ('video', models.FileField(upload_to='profile/video')),
                ('instrument', models.CharField(choices=[('H', '현악기'), ('G', '관악기'), ('T', '타악기'), ('ETC', '기타')], max_length=3)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('followers', models.ManyToManyField(blank=True, related_name='_userprofile_followers_+', to='core.UserProfile')),
                ('followings', models.ManyToManyField(blank=True, related_name='_userprofile_followings_+', to='core.UserProfile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SM_MDPICK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('artists', models.ManyToManyField(blank=True, related_name='md_artists', to='core.UserProfile')),
                ('bg_mdpick', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.BG_MDPICK')),
                ('items', models.ManyToManyField(blank=True, related_name='md_items', to='core.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('accepted', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=50)),
                ('amount', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('ordered_detail', models.IntegerField(blank=True, choices=[(1, '1단계'), (2, '2단계'), (3, '3단계'), (4, '4단계')], null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('quantity', models.IntegerField(default=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orderitem_author', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='core.OrderItem'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Payment'),
        ),
        migrations.AddField(
            model_name='order',
            name='special_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='special_address', to='core.Address'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=50)),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(blank=True, choices=[('H', '현악기'), ('G', '관악기'), ('T', '타악기'), ('ETC', '기타')], max_length=2, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='article/image')),
                ('video', models.FileField(blank=True, null=True, upload_to='article/video')),
                ('slug', models.SlugField(blank=True, null=True)),
                ('article_password', models.CharField(blank=True, max_length=20, null=True)),
                ('embedurl', models.CharField(max_length=200)),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
                ('orderitem', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article_orderitem', to='core.OrderItem')),
            ],
        ),
    ]
