from django.db import models

# Create your models here.
# catalogue/models.py
from django.db import models
from django.dispatch import receiver
from django.utils import timezone # استيراد أداة الوقت من ديجانغو
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=500)
    
    # يبقى كما هو: يسجل وقت إضافة الكتاب للمكتبة لأول مرة
    created_at = models.DateTimeField(auto_now_add=True)
    
    # تغيير: حقل عادي لا يتحدث تلقائياً إلا عندما نأمره بذلك
    last_read = models.DateTimeField(default=timezone.now)

    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        db_table = 'catalogue_book'


from django.contrib.auth.models import User

class Comment(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"تعليق من {self.user.username} على {self.book.title}"
    

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at'] 
        unique_together = ('user', 'book') 

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # أنشئ بروفايل برابط صورة افتراضي
        Profile.objects.create(user=instance, image_url="https://cdn-icons-png.flaticon.com/512/149/149071.png")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()




class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"سلة {self.user.username}"

    # دالة لحساب المجموع الكلي للسلة
    def get_total_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

    # دالة لحساب سعر الكمية من كتاب واحد
    def get_total_item_price(self):
        return self.quantity * self.book.price
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False) 

    def __str__(self):
        return f"طلب رقم {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) 