import secrets
from django.core.mail import send_mail

from celery import shared_task



@shared_task
def add(x, y):
    return x + y

@shared_task
def user_email_verification_flow_async(user_email, user_token, host) -> None:    
    mail_message = 'This is your email verification link'
    send_mail(
        'Email Verification at Deli Bookmarking Service',
         f'{mail_message} http://{host}/users/verification/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)

@shared_task
def user_password_reset_send_async(user_email, user_token, host) -> None:
    mail_message = 'This is your Password reset link'
    send_mail(
        'Password Reset at Deli Bookmarking Services',
         f'{mail_message} http://{host}/users/password/reset/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)

@shared_task
def generate_token_async() -> str:
        token = secrets.token_urlsafe(50)
        return token