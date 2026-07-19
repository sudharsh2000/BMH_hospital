from django.urls import path
from accounts.views import SignupView,LogoutView,LoginView,RefreshTokenView,VerifyOtpView,ResendOtpView,ForgotPasswordView,ConfirmPasswordView, \
 setPasswordView
urlpatterns=[

    path('signup/',SignupView.as_view(),name='signup'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('login/',LoginView.as_view(),name='login'),
    path('refresh/',RefreshTokenView.as_view(),name='refresh'),
    path('verify/otp/',VerifyOtpView.as_view(),name='verify_otp'),
    path('resend-otp/',ResendOtpView.as_view(),name='resend-otp'),
    path('forgot-password/',ForgotPasswordView.as_view(),name='forgot_password'),
    path('confirm-password/',ConfirmPasswordView.as_view(),name='confirm_password'),
    path('setpassword/', setPasswordView.as_view(), name='setPassword'),

]
