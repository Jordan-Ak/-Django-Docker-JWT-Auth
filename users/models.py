import secrets
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify

from common.models import BaseModel
from users.managers import CustomUserManager
from users.tasks import generate_token_async
# Create your models here.

class CustomUser(AbstractUser, BaseModel):
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=False)
    slug_username = models.CharField(_('Slug Username'), max_length = 150, blank = True)

    is_verified_email = models.BooleanField(_('is verified email'), default = False)
    is_verified = models.BooleanField(_('is verified'), default = False,)
    password_last_changed = models.DateTimeField(_('password last changed'), null = True)
    email_verification_token = models.CharField(_('email token'), null = True, max_length = 255)
    email_token_sent_at = models.DateTimeField(_('email token sent at'), null = True)
    password_reset_token = models.CharField(_('password reset token'), null = True, max_length = 255)
    password_reset_sent_at = models.DateTimeField(_('password reset sent at'), null = True)
        

    date_joined = None

    objects = CustomUserManager()

    def generate_slug_username(self) -> str:
        self.slug_username = slugify(self.username)
        self.save()
    
    def generate_token(self) -> str:
        token = secrets.token_urlsafe(50)
        return token
    
    def generate_email_verification_token(self) -> None:
        self.email_verification_token = generate_token_async.apply_async().get()#self.generate_token()
        self.email_token_sent_at = timezone.now()
        self.save()
    
    def generate_password_verification_token(self) -> None:
        self.password_reset_token = generate_token_async.apply_async().get()#self.generate_token()
        self.password_reset_sent_at = timezone.now()
        self.save()
    
    def has_email_verification_token_expired(self) -> bool:
        return timezone.now() > self.email_token_sent_at + timedelta(hours = 5)

    def has_password_reset_token_expired(self) -> bool:
        return timezone.now() > self.password_reset_sent_at + timedelta(hours = 5)

    def confirm_email(self) -> None:
        self.email_verification_token = None
        self.email_token_sent_at = None
        self.is_verified_email = True
        self.save()
    
    def confirm_reset(self) -> None:
        self.password_reset_token = None
        self.password_reset_sent_at = None
        self.password_last_changed = timezone.now()
        self.save()

    def __str__(self) -> str:
        return self.username

def profile_photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_<username>/<filename>
    return 'profile_{0}/{1}'.format(instance.username,filename)

class Profile(models.Model):
    username = models.CharField(max_length = 150)
    profile_photo = models.ImageField(_('Profile Photo'), upload_to = profile_photo_directory_path,)
    contact = models.CharField(max_length = 200, blank = True)
    bio = models.CharField(max_length = 200, blank = True)
    #private = models.BooleanField(default = False) This field should be added to custom user instead
    #favorite_tags = models.
    