from django.urls import path
from . import views
from .views import EmailLogin ,EmailSignUp, LogoutView , AccountType , CreatorProfileUpdate , AccountIntegration , AccountIntegrationUpdate , BrandProfileUpdate

urlpatterns = [

    path("" , views.home , name='home'),
    path("login/" , EmailLogin.as_view() , name="login"),
    path("logout/" , LogoutView.as_view(next_page = 'login'), name="logout"),
    path("signup/" , EmailSignUp.as_view() , name="signup"),
    path("instagram_integration/" , AccountIntegration.as_view() , name="instagram_integration"),
    path("instagram_integration_update/<int:pk>/" , AccountIntegrationUpdate.as_view() , name="instagram_integration_update"),
    path("integration_dashboard/<int:pk>/" , views.integration_dashboard , name="integration_dashboard"),
    path("creator_proposal_view/<int:pk>/" , views.creator_proposal_view , name='creator_proposal_detail' ),

    path("account_selection/", AccountType.as_view() , name="account_selection"),
    path("update_profile/creator/<int:pk>/" , CreatorProfileUpdate.as_view(), name="creator_profile_update" ),
    path("update_profile/brand/<int:pk>/" , BrandProfileUpdate.as_view(), name="brand_profile_update" ),
]