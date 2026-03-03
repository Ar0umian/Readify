from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill'}))
    image_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'رابط صورتك'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill'}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ['username', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control rounded-pill'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image_url']
        labels = {
            'image_url': 'رابط الصورة الشخصية'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_url'].widget.attrs.update({
            'class': 'form-control rounded-pill',
            'placeholder': 'https://example.com/my-photo.jpg'
        })