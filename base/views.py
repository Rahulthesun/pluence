from django.forms import BaseModelForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse_lazy , reverse
from django.http import HttpResponse 

from users.forms import EmailUserCreationForm
from .forms import AccountTypeForm , AccountIntegrationForm
from users.models import EmailUser
from .models import CreatorProfile ,BrandProfile , BrandProposal , InstagramAccountDashBoard



from django.contrib.auth.mixins import UserPassesTestMixin , LoginRequiredMixin
from django.contrib.auth import login , authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView , FormView , UpdateView
from django.contrib.auth.views import LoginView , LogoutView

import requests

code = ""
client_id = '2221760501509247'
client_secret = '5fa1b8b40763fa9c9a0d699af2ca19d2'
token_exchange_url = 'https://api.instagram.com/oauth/access_token'
instagram_auth_url = 'https://api.instagram.com/oauth/authorize'
scope = 'instagram_basic,instagram_manage_insights'
response_type = 'code'


# Create your views here.


@login_required
def home(request):
    creator_account = CreatorProfile.objects.filter(user = request.user)
    brand_account = BrandProfile.objects.filter(user = request.user)
    context = {}
    if creator_account.exists():
        proposals = BrandProposal.objects.filter(creator = creator_account[0])
        ig_account = InstagramAccountDashBoard.objects.filter(creator = creator_account[0])
        if proposals.exists():
            context['proposals'] = proposals

        if ig_account.exists():
            context['ig_account'] = ig_account[0]
        
        elif not ig_account.exists():
            context['ig_account'] = None

        else :
            context['proposals'] = None
        context['account'] = creator_account[0]
        template = 'base/creator_home.html'
    elif brand_account.exists():
        proposals = BrandProposal.objects.filter(brand = brand_account[0])
        search_query = request.GET.get("search" , "")
        sort_query = request.GET.get("sort" , "")
        if not search_query:
            if sort_query =="all":
                creator_accounts = InstagramAccountDashBoard.objects.all()
            elif sort_query == "followers-asc" :
                creator_accounts = InstagramAccountDashBoard.objects.all().order_by("followers")
            else:
                creator_accounts = InstagramAccountDashBoard.objects.all().order_by("-followers")
        
        elif search_query:
            if sort_query == 'all':
                creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query)
            if sort_query == 'followers-asc':
                creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query).order_by('followers')
            else:
                creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query).order_by('-followers')


        if proposals.exists():
            context['proposals'] = proposals
        else:
            context['proposals'] = None
            
        context['creators'] = creator_accounts
        context['account'] = brand_account[0]
        template = 'base/brand_home.html'
    elif not creator_account.exists() and not brand_account.exists():        
        return redirect(reverse_lazy("account_selection"))
    return render(request , template , context)
    

class EmailLogin(LoginView):
    redirect_authenticated_user = True
    template_name = "base/login.html"
    context_object_name = "form"

    def get_success_url(self):
        return reverse_lazy("home")

class EmailSignUp(UserPassesTestMixin , FormView):
    form_class = EmailUserCreationForm
    template_name = "base/signup.html"

    def get_success_url(self):
        return reverse_lazy("account_selection")
    
    def form_valid(self , form):
        user = form.save()
        if user is not None:
            login(self.request , user)
        return super(EmailSignUp,self).form_valid(form)    
    
    def test_func(self):
        return self.request.user.is_anonymous
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy("home"))
    

class AccountType(UserPassesTestMixin ,FormView,LoginRequiredMixin):
    form_class = AccountTypeForm
    template_name = "base/account_selection.html"
    success_url = reverse_lazy("home")
    
    def test_func(self):
        creator_account = CreatorProfile.objects.filter(user = self.request.user)
        brand_account = BrandProfile.objects.filter(user = self.request.user)
        if brand_account.exists() or creator_account.exists() :
            return False
        else:
            return True
        
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy("home"))

    def form_valid(self, form):
        account_type = form.cleaned_data['account_type']
        if account_type == "brand":
            account,created = BrandProfile.objects.get_or_create(user = self.request.user)
        else:
            account,created = CreatorProfile.objects.get_or_create(user = self.request.user)
        account.active = True
        account.save()
        return super().form_valid(form)
    

class CreatorProfileUpdate(LoginRequiredMixin , UpdateView):
    model = CreatorProfile
    fields = ['name' , 'bio' ,'contact_email' , 'website' ]
    template_name = "base/update_profile.html"
    success_url= reverse_lazy("home")

class BrandProfileUpdate(LoginRequiredMixin , UpdateView):
    model = BrandProfile
    fields = ['brand_name' , 'email' , 'about']
    template_name = "base/update_profile.html"
    success_url = reverse_lazy('home')

def integration_dashboard(request , pk):
    dashboard = get_object_or_404(InstagramAccountDashBoard , id=pk)
    context = {
        'dashboard': dashboard,
    }
    return render(request , 'base/integration_dashboard.html' , context)


class AccountIntegration(LoginRequiredMixin ,FormView):
    form_class = AccountIntegrationForm
    template_name = 'base/account_integration.html'
    success_url = reverse_lazy("home")
    

    def form_valid(self, form):
        creator = get_object_or_404(CreatorProfile ,user = self.request.user)
        avg_rate = (form.cleaned_data['story_rates'] + form.cleaned_data['reel_rates']) // 2
        dashboard, created = InstagramAccountDashBoard.objects.get_or_create(
            creator = creator,
            tags = form.cleaned_data['tags'],
            username = form.cleaned_data['username'],
            followers = form.cleaned_data['followers'],
            reach = form.cleaned_data['reach'],
            profile_link_clicks = form.cleaned_data['profile_link_clicks'],
            engagement = form.cleaned_data['engagement'],
            audience_country = form.cleaned_data['audience_country'],
            story_rates = form.cleaned_data['story_rates'],
            reel_rates = form.cleaned_data['reel_rates'],
            average_rate = avg_rate
            )
        self.id = dashboard.id
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse("integration_dashboard" , kwargs= {"pk": self.id})
    
class AccountIntegrationUpdate(LoginRequiredMixin , UpdateView):
    model = InstagramAccountDashBoard
    form_class = AccountIntegrationForm
    template_name = 'base/account_integration.html'



    def get_success_url(self):
        id = self.kwargs.get('pk')
        return reverse("integration_dashboard" , kwargs= {"pk": id})
    
    
def creator_proposal_view(request , pk):
    proposal = get_object_or_404(BrandProposal , id = pk )
    context = {
        'proposal' : proposal
    }

    return render(request , 'base/creator_proposal_view.html' , context)

    
