from pyexpat.errors import messages

from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Profile
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Create your views here.

# accounts/views.py


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages as django_messages
from .forms import UserUpdateForm, ProfileUpdateForm

from catalogue.models import Order

from catalogue.models import Comment, UserHistory


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()#(commit=False)
            #user.set_password(form.cleaned_data['password'])
            #user.save()

            image_link = request.POST.get('image_url') #or form.cleaned_data.get('image_url')
            print(f"Image Link Captured: {image_link}")

            if not image_link or image_link.strip() == "":
                image_link = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

            Profile.objects.filter(user=user).delete() 
            Profile.objects.create(user=user, image_url=image_link)

            #profile.save()

            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})





def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required(login_url='login') # حماية الصفحة
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})




def profile_view(request):
    user = request.user
    user_comments = Comment.objects.filter(user=user).order_by('-created_at')[:5]
    
    history = UserHistory.objects.filter(user=user).order_by('-viewed_at')[:6]
    orders = Order.objects.filter(user=user).order_by('-created_at')

    return render(request, 'accounts/profile.html', {
        'user_comments': user_comments,
        'history': history,
        'orders': orders
    })


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    django_msgs = messages

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile) 
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })

def change_password(request):
    if request.method == 'POST':
        # النموذج يطلب (الباسورد القديم + الجديد + تأكيد الجديد)
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # أهم خطوة: تحديث الجلسة لكي لا يتم تسجيل خروج المستخدم بعد تغيير الباسورد
            update_session_auth_hash(request, user)
            django_messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('profile')
        else:
            django_messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # حذف المستخدم والبروفايل وكل بياناته
        django_messages.warning(request, "تم حذف الحساب بنجاح.")
        return redirect('index')
    
    return redirect('profile') # حماية في حال الوصول للرابط عبر GET