from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import ResetPasswordView
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView,PasswordResetCompleteView

from .views import EmailLogin ,EmailSignUp, LogoutView , AccountType , CreatorProfileUpdate , AccountIntegration , AccountIntegrationUpdate , BrandProfileUpdate, CreateBrandProposal ,CreateTiktokBrandProposal, DashboardImageUpdate , EmailVerification , BrandAccountSubscription,EmailVerificationView
from .views import TiktokDashboardEdit

urlpatterns = [

    path("" , views.landing_page , name="landing_page"),
    path("creator/" , views.landing_page_creator , name="landing_page_creator"),
    path("pricing/" , views.landing_page_pricing , name="landing_page_pricing"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-and-conditions/", views.terms_and_conditions, name="terms_and_conditions"),
    
    path("home/" , views.home , name='home'),
    path("home/<slug:slug>/" , views.home , name='home_with_slug'),
    path("login/" , EmailLogin.as_view() , name="login"),
    path("logout/" , LogoutView.as_view(next_page = 'login'), name="logout"),
    path("signup/" , EmailSignUp.as_view() , name="signup"),
    path("instagram_integration/" , AccountIntegration.as_view() , name="instagram_integration"),
    path("instagram_integration_update/<int:pk>/" , AccountIntegrationUpdate.as_view() , name="instagram_integration_update"),
    path("instagram_integration/dashboard_image/update/<int:pk>/" , DashboardImageUpdate.as_view() , name="dashboard_image_update"),
    
    path("integration_dashboard/<int:pk>/" , views.integration_dashboard , name="integration_dashboard"),
    path("creator_proposal_view/<int:pk>/" , views.creator_proposal_view , name='creator_proposal_detail' ),
    path("creator_proposal_view/<int:pk>/<slug:slug>/" , views.creator_proposal_view , name='creator_proposal_detail_with_slug' ),
    path("brand_proposal_view/<int:pk>/" , views.brand_proposal_view , name='brand_proposal_detail' ),
    path("brand/create_brand_proposal/<int:creator_id>/" , CreateBrandProposal.as_view() , name='create_brand_proposal' ),
    path("brand/create_brand_proposal/tiktok/<int:creator_id>/" , CreateTiktokBrandProposal.as_view() , name='create_tiktok_brand_proposal' ),
    path("creator/brand_proposal/accept/<int:proposal_id>/" , views.accept_brand_proposal , name='accept_brand_proposal' ),
    path("creator/brand_proposal/accept/<int:proposal_id>/<slug:slug>/" , views.accept_brand_proposal , name='accept_brand_proposal_with_slug' ),
    path("creator/brand_proposal/reject/<int:proposal_id>/" , views.reject_brand_proposal , name='reject_brand_proposal' ),
    path("creator/brand_proposal/reject/<int:proposal_id>/<slug:slug>/" , views.reject_brand_proposal , name='reject_brand_proposal_with_slug' ),
    path("creator/active_proposals/<int:creator_id>/" , views.creator_active_proposals ,name='creator_active_proposals'),
    path("creator/payment_dashboard/<int:creator_id>/" , views.creator_payment_dashboard ,name='creator_payment_dashboard'),
    path("brand/proposal_payment/<int:proposal_id>/" , views.brand_proposal_payment ,name='brand_proposal_payment'),
    path('brand/proposal/<int:brand_id>/', views.get_brand_proposals, name='brand_proposals'),
    path("successfull_payment/<int:proposal_id>/" , views.successfull_payment  , name="successfull_payment"),
    path("failed_payment/<int:brand_id>/" , views.payment_failed  , name="payment_failed"),
    path("creator/content_approval/<int:proposal_id>/" , views.content_approval_process   , name="content_approval"),
    path("brand/pending_content_approval/" , views.brand_pending_approval_view   , name="pending_content_approval"),
    path("brand/pending_content_review/<int:proposal_id>/" , views.brand_content_review   , name="brand_content_review"),
    path("brand/approve_content/<int:proposal_id>/" , views.approve_content   , name="approve_content"),
    


    path("account_selection/", AccountType.as_view() , name="account_selection"),
    path("brand_subscription/<int:brand_id>/", BrandAccountSubscription.as_view() , name="brand_subscription"),
    path("brand_subscription_payment/<int:brand_id>/", views.brand_subscription_payment , name="brand_subscription_payment"),
    path("brand_subscription_activation/<int:brand_id>/", views.brand_subscription_activation, name="brand_subscription_activation"),
    path("update_profile/creator/<int:pk>/" , CreatorProfileUpdate.as_view(), name="creator_profile_update" ),
    path("update_profile/brand/<int:pk>/" , BrandProfileUpdate.as_view(), name="brand_profile_update" ),
    path("email_verification/<int:verify_id>/<int:pk>/" , EmailVerification.as_view(), name="email_verification" ),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='base/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'),
         name='password_reset_complete'),
     
     #Can't edit the root urls for just these URLS , because they are configured to tiktok api 
     path("tiktok/authorize/" , views.tiktok_authorize, name="tiktok_authorize"),
     path("tiktok/get-data/<int:dash_id>/" , views.tiktok_user_data , name="tiktok_get_data"),
     path("tiktok/edit_dashboard/<int:pk>/" , TiktokDashboardEdit.as_view() , name="edit_tiktok_dashboard"),
     path('verify-email/<str:pk>/<int:verify_id>/', EmailVerificationView.as_view(), name='EmailVerificationView'),

]

if settings.DEBUG == True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
