from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from users.models import Profile

def validate_password(password) -> str:
    min_length = 7

    if len(password) < min_length:
        raise serializers.ValidationError(_(f'Your password must be at least {min_length} characters'))
    
    elif not any(char.isdigit() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one number.'))
    
    elif not any(char.isalpha() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one letter.'))

    return password

def validate_password_match(pass1, pass2) -> None:
     if pass1 != pass2:
            raise serializers.ValidationError(_('Passwords do not match'))

def validate_unique_email(email):
    try:
        get_user_model().objects.get(email = email.lower())
    except ObjectDoesNotExist:
        pass #Email is unique
    else:
        raise serializers.ValidationError("This email is already in use.")

def user_email_verification_flow(user_email, user_token, host) -> None:    
    mail_message = 'This is your email verification link'
    send_mail(
        'Email Verification at Deli Bookmarking Service',
         f'{mail_message} http://{host}/users/verification/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)


def user_create(username, email, password) -> get_user_model:
    user : get_user_model = get_user_model().objects.create(username = username, email = email)
    user.set_password(password)
    
    user.save()

    user.generate_email_verification_token()
    user.generate_slug_username()
    token = user.email_verification_token
    #user_email_verification_flow(email, token, host)
    
    profile_create(user)
    return user

def user_update(instance, **serializer_data) -> get_user_model:
    instance.username = serializer_data.get('username', instance.username)
    instance.first_name = serializer_data.get('first_name', instance.first_name)
    instance.last_name = serializer_data.get('last_name', instance.last_name)
    instance.save()    
    instance.generate_slug_username()

    return instance

def user_retrieve_email(email) -> get_user_model:
    try:
        user: get_user_model = get_user_model().objects.get(email = email)
    except ObjectDoesNotExist:
        raise NotFound() # Not necessary to implement now   ## None value returned instead an exception because users shouldn't be able to guess emails used.
    return user


def user_retrieve_email_token(token) -> get_user_model:
    try:
        user: get_user_model = get_user_model().objects.get(email_verification_token = token)
    
    except ObjectDoesNotExist:
        raise NotFound()
    
    return user

def user_retrieve_password_reset(token) -> get_user_model:
    try:
        user : get_user_model = get_user_model().objects.get(password_reset_token = token)
    
    except ObjectDoesNotExist:
        raise NotFound()
    
    return user

def user_email_verification_confirm(user) -> None:
    if user.has_email_verification_token_expired():
        raise PermissionDenied(_('Resend email verification this token has expired'))
    
    elif user.is_verified_email:
        raise serializers.ValidationError(_('User is already verified'))
   
    else:
        user.confirm_email()

def user_email_verified_check(user) -> None:
    if user.is_verified_email:
        raise serializers.ValidationError(_('Your email is already verified'))

def user_password_change(user, **serializer_data) -> None:
    if not user.check_password(serializer_data['old_password']):
        raise serializers.ValidationError(_('Old password is incorrect.'))
    
    user.set_password(serializer_data['password'])
    user.password_last_changed = timezone.now()
    user.save()

def user_password_reset_send(user_email, user_token, host) -> None:
    mail_message = 'This is your Password reset link'
    send_mail(
        'Password Reset at Deli Bookmarking Services',
         f'{mail_message} http://{host}/users/password/reset/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)

def user_password_reset_validity(user) -> None:
    if user.has_password_reset_token_expired():
        raise PermissionDenied(detail=_("Password reset token has expired."))

def user_password_reset_change(user, new_password) -> None:
    user.confirm_reset()
    user.set_password(new_password)
    user.save()

def user_all_refresh_blacklist(user) -> None:
    id = user.id
    tokens_to_blacklist = OutstandingToken.objects.filter(user_id = user.id)
    for token_b in tokens_to_blacklist:
        token_check = BlacklistedToken.objects.filter(token = token_b)
        if not token_check:
            blacklist_token = BlacklistedToken.objects.create(token = token_b)


def profile_create(user) -> None:
    profile = Profile.objects.create(username = user.username)
    profile.save()

def profile_retrieve_user(username) -> Profile:
    try:
        profile = Profile.objects.get(username = username)
    except ObjectDoesNotExist:
        raise NotFound(detail = "This user does not exist.")
    return profile

def profile_user_check(user, username) -> None:
    if not user.username == username:
        raise PermissionDenied(detail = "This user cannot edit this profile.")

def profile_update(instance, **serializer_data) -> Profile:
    instance.profile_photo = serializer_data.get('profile_photo', instance.profile_photo)
    instance.contact = serializer_data.get('contact', instance.contact)
    instance.bio = serializer_data.get('bio', instance.bio)
    
    instance.save()
    return instance
