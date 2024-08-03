from django.urls import path,include
from . import views

from .views import EmailLogin ,EmailSignUp, LogoutView , AccountType , CreatorProfileUpdate , AccountIntegration , AccountIntegrationUpdate , BrandProfileUpdate,get_proposal_details,CreateBrandProposal



urlpatterns = [

    path("" , views.home , name='home'),
    path("login/" , EmailLogin.as_view() , name="login"),
    path("logout/" , LogoutView.as_view(next_page = 'login'), name="logout"),
    path("signup/" , EmailSignUp.as_view() , name="signup"),
    path("instagram_integration/" , AccountIntegration.as_view() , name="instagram_integration"),
    path("instagram_integration_update/<int:pk>/" , AccountIntegrationUpdate.as_view() , name="instagram_integration_update"),
    path("integration_dashboard/<int:pk>/" , views.integration_dashboard , name="integration_dashboard"),
    path("creator_proposal_view/<int:pk>/" , views.creator_proposal_view , name='creator_proposal_detail' ),
    path("create_brand_proposal/<int:creator_id>/" , CreateBrandProposal.as_view() , name='create_brand_proposal' ),
    path("brand_proposal/accept/<int:proposal_id>/" , views.accept_brand_proposal , name='accept_brand_proposal' ),
    path("brand_proposal/reject/<int:proposal_id>/" , views.reject_brand_proposal , name='reject_brand_proposal' ),
    path("creator/active_proposals/<int:creator_id>/" , views.creator_active_proposals ,name='creator_active_proposals'),
    path("creator/payment_dashboard/<int:creator_id>/" , views.creator_payment_dashboard ,name='creator_payment_dashboard'),
    path("brand/proposal_payment/<int:proposal_id>/" , views.brand_proposal_payment ,name='brand_proposal_payment'),

    path("account_selection/", AccountType.as_view() , name="account_selection"),
    path("update_profile/creator/<int:pk>/" , CreatorProfileUpdate.as_view(), name="creator_profile_update" ),
    path("update_profile/brand/<int:pk>/" , BrandProfileUpdate.as_view(), name="brand_profile_update" ),
    path('proposal/<int:pk>/', get_proposal_details, name='proposal_details'),
]