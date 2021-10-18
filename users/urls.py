from django.urls import path

from users.views import ProfileView, UserAdminDetailView, UserAdminListView, UserCreateView, UserDetailView, UserEmailVerificationConfirmView, UserPasswordChangeView, UserPasswordResetConfirmView, UserPasswordResetView, UserResendEmailVerificationView

urlpatterns = [
    path('signup/', UserCreateView.as_view(), name = 'users-signup'),
    path('me/', UserDetailView.as_view(), name = 'users-detail'),
    #Admin user urls
    path('admin/list', UserAdminListView.as_view(), name = 'users-admin-list'),
    path('admin/<str:id>/', UserAdminDetailView.as_view(), name = 'users-admin-detail'),
    #Email verification urls
    path('verification/confirm/<str:email_verification_token>/',
              UserEmailVerificationConfirmView.as_view(), name = 'users-email-confirm'),
    path('verification/resend/', UserResendEmailVerificationView.as_view(), name = 'users-email-resend'),
    #Users password urls
    path('password/change/', UserPasswordChangeView.as_view(), name = 'users-password-change'),
    path('password/reset/', UserPasswordResetView.as_view(), name = 'users-password-reset'),
    path('password/reset/confirm/<str:password_reset_token>/',
              UserPasswordResetConfirmView.as_view(), name = 'users-password-reset-confirm'),
    path('profile/<str:username>/', ProfileView.as_view(), name = 'users-profile'),
]