from django.urls import path
from accounts.views.wallet import my_wallet
from accounts.views.account import *
from accounts.views.notification import subscribe, unsubscribe
from accounts.views.password import password_reset_request, password_change, passwordResetConfirm, password_reset_sent
from accounts.views.qualification import create_qualification, update_qualification, qualifications, delete_qualification
from accounts.views.relative import create_relative, update_relative, relatives, relative, delete_relative


app_name = "accounts"
urlpatterns = [
    path("", get_accounts, name="accounts"),
    path("dashboard", get_me, name="me"),
    path("register", register, name="register"),
    path('login', custom_login, name='login'),
    path('logout', custom_logout, name='logout'),
    path("dashboard/wallet", my_wallet, name="wallet"),
    path('register/success', activation_sent, name='success'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('confirm/email/<uidb64>/<token>', confirm_email, name='confirm-email'),

    path("password/reset", password_reset_request, name="password-reset"),
    path('password/success', password_reset_sent, name='password-reset-sent'),
    path('password/reset/<uidb64>/<token>', passwordResetConfirm, name='password-reset-confirm'),

    path('details/<username>', user_details, name="user"),
    path('update/subscribe', subscribe, name="subscribe"),
    path('update/unsubscribe', unsubscribe, name="unsubscribe"),
    path('update/profile', account_update, name="profile-update"),
    path('update/contact', general, name="contact-update"),
    path('update/password', password_change, name="password-update"),
    path('update/identitfication', identitification, name="verify"),
    path('update/social', add_social_links, name="update-social-links"),

    path('qualifications', qualifications, name="qualifications"),
    path('qualification/update/<id>', update_qualification, name="update-qualification"),
    path('qualification/delete/<id>', delete_qualification, name="delete-qualification"),
    path('qualification/create', create_qualification, name="create-qualification"),

    path('relatives', relatives, name="relatives"),
    path('relatives/<uuid:id>', relative, name="relative"),
    path('relative/update/<uuid:id>', update_relative, name="update-relative"),
    path('relative/delete/<uuid:id>', delete_relative, name="delete-relative"),
    path('relative/create', create_relative, name="create-relative"),

]
