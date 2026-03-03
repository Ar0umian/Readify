from django.db import models
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image_url = models.URLField(default="https://via.placeholder.com/150") # رابط الصورة

    def __str__(self):
        return f"بروفايل {self.user.username}"
    
    