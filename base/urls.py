from django.urls import path,include
from . import views

from .views import EmailLogin ,EmailSignUp, LogoutView , AccountType , CreatorProfileUpdate , AccountIntegration , AccountIntegrationUpdate , BrandProfileUpdate, CreateBrandProposal , DashboardImageUpdate

urlpatterns = [

    path("" , views.landing_page , name="temp_landing"),
    path("home/" , views.home , name='home'),
    path("login/" , EmailLogin.as_view() , name="login"),
    path("logout/" , LogoutView.as_view(next_page = 'login'), name="logout"),
    path("signup/" , EmailSignUp.as_view() , name="signup"),
    path("instagram_integration/" , AccountIntegration.as_view() , name="instagram_integration"),
    path("instagram_integration_update/<int:pk>/" , AccountIntegrationUpdate.as_view() , name="instagram_integration_update"),
    path("instagram_integration/dashboard_image/update/<int:pk>/" , DashboardImageUpdate.as_view() , name="dashboard_image_update"),
    
    path("integration_dashboard/<int:pk>/" , views.integration_dashboard , name="integration_dashboard"),
    path("creator_proposal_view/<int:pk>/" , views.creator_proposal_view , name='creator_proposal_detail' ),
    path("create_brand_proposal/<int:creator_id>/" , CreateBrandProposal.as_view() , name='create_brand_proposal' ),
    path("brand_proposal/accept/<int:proposal_id>/" , views.accept_brand_proposal , name='accept_brand_proposal' ),
    path("brand_proposal/reject/<int:proposal_id>/" , views.reject_brand_proposal , name='reject_brand_proposal' ),
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
    path("update_profile/creator/<int:pk>/" , CreatorProfileUpdate.as_view(), name="creator_profile_update" ),
    path("update_profile/brand/<int:pk>/" , BrandProfileUpdate.as_view(), name="brand_profile_update" ),
    
]