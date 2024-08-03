from django.urls import path
from .views import get_proposal


urlpatterns=[
path('proposal/<int:pk>/', get_proposal, name='proposal_details'),
]