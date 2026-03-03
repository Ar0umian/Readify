from email.mime.image import MIMEImage
import random

from django.shortcuts import get_object_or_404, render, redirect
import qrcode
import qrcode
import io
import base64
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order
from django.contrib import messages as django_messages
from django.conf import settings

# Create your views here.
def index(request):
    # أحدث الكتب المضافة
    latest_books = Book.objects.order_by('-created_at')[:4]
    
    # الكتب التي تم النقر على تفاصيلها مؤخراً
    recent_books = Book.objects.order_by('-last_read')[:4]
    
    return render(request, 'catalogue/index.html', {
        'latest_books': latest_books,
        'recent_books': recent_books
    })

# catalogue/views.py
from django.shortcuts import render, get_object_or_404
from .models import Book, UserHistory
from django.utils import timezone
from .models import Book, Comment
#from .forms import CommentForm
from decimal import Decimal


from django.shortcuts import render, get_object_or_404, redirect
from .models import Book

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # جلب التعليقات مرتبة من الأحدث للأقدم
    comments = book.comments.all().order_by('-created_at')
    if request.user.is_authenticated:
        # هذه الدالة تبحث عن الكتاب، إذا وجدته تحدث وقت الزيارة، وإذا لم تجده تنشئه
        UserHistory.objects.update_or_create(
            user=request.user, 
            book=book
        )

    if request.method == 'POST':
        # التحقق من تسجيل الدخول قبل الحفظ
        if request.user.is_authenticated:
            comment_text = request.POST.get('text')
            if comment_text:
                Comment.objects.create(
                    book=book,
                    user=request.user,
                    text=comment_text
                )
                return redirect('book_detail', book_id=book.id)
        
    
        else:
            return redirect('login') # توجيه غير المسجل لصفحة الدخول

    return render(request, 'catalogue/details.html', {
        'book': book,
        'comments': comments
    })



# books/views.py
from django.shortcuts import get_object_or_404, redirect
from .models import Book, Cart, CartItem
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    if not request.user.is_authenticated:
        django_messages.info(request, "يرجى تسجيل الدخول أولاً لتتمكن من إضافة الكتب للسلة.")
        return redirect('login')
        
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    # الحصول على سلة المستخدم أو إنشاؤها إذا كانت أول مرة
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all() # جلب جميع الكتب داخل السلة
    
    return render(request, 'checkout/cart.html', {
        'cart': cart,
        'items': items
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

from .models import Order, OrderItem

# views.py
@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('cart_detail') 

    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price(),
        is_paid=True 
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            book=item.book,
            quantity=item.quantity,
            price_at_purchase=item.book.price 
        )

    subtotal = Decimal(str(order.total_price))
    tax_amount = subtotal * Decimal('0.05')
    final_total = subtotal + tax_amount

    qr_data = f"Readify Order #{order.id}\nTotal: {final_total} SAR"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'order': order,
        'items': order.items.all(),
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'final_total': final_total,
        'qr_code': qr_base64,
    }

    try:
        send_invoice_email(order, context)
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الإيميل: {e}")

    cart.items.all().delete()

    return render(request, 'checkout/order_success.html', {'order': order})

# views.py
@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    subtotal = Decimal(str(order.total_price))
    tax_amount = subtotal * Decimal('0.05')
    final_total = subtotal + tax_amount

    qr_data = f"Order #{order.id}"
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(qr_data)
    img = qr.make_image()
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'order': order,
        'items': order.items.all(),
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'final_total': final_total,
        'qr_code': qr_base64,
    }
    return render(request, 'checkout/invoice.html', context)


def send_invoice_email(order, context):
    subject = f'فاتورة شراء من Readify - طلب رقم #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = order.user.email

    html_content = render_to_string('checkout/email_invoice.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")

    if 'qr_code' in context:
        # تحويل الـ Base64 لبيانات ثنائية (Binary)
        import base64
        image_data = base64.b64decode(context['qr_code'])
        
        # إنشاء كائن الصورة وتحديد معرف لها (CID)
        mime_image = MIMEImage(image_data)
        mime_image.add_header('Content-ID', '<qr_code>') # تأكدي من الأقواس < >
        msg.attach(mime_image)

    msg.send()


def all_books(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(title__icontains=query) 
    else:
        books = Book.objects.all()
    
    return render(request, 'catalogue/all_books.html', {'books': books, 'query': query})


def random_book_redirect(request):
    book_ids = Book.objects.values_list('id', flat=True)
    if book_ids:
        random_id = random.choice(book_ids)
        return redirect('book_detail', book_id=random_id) 
    return redirect('all_books') 


@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()
    django_messages.success(request, "تم حذف الفاتورة بنجاح.")
    return redirect('profile')