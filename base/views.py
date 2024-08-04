from django.forms import BaseModelForm
from django.http.response import HttpResponseRedirect
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse_lazy , reverse
from django.http import HttpResponse 

from users.forms import EmailUserCreationForm
from .forms import AccountTypeForm , AccountIntegrationForm , BrandProposalForm
from users.models import EmailUser
from .models import CreatorProfile ,BrandProfile , BrandProposal , InstagramAccountDashBoard



from django.contrib.auth.mixins import UserPassesTestMixin , LoginRequiredMixin
from django.contrib.auth import login , authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView , FormView , UpdateView
from django.contrib.auth.views import LoginView , LogoutView
from django.contrib import messages

import requests , datetime , decimal
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm
import sib_api_v3_sdk


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

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
        proposals = BrandProposal.objects.filter(creator = creator_account[0] , proposal_status = BrandProposal.Proposal_Status.REQUESTED)
        ig_account = InstagramAccountDashBoard.objects.filter(creator = creator_account[0])
        active_proposals = BrandProposal.objects.filter(creator = creator_account[0] , proposal_status = BrandProposal.Proposal_Status.PAID)
        
        if active_proposals.exists():
            context['active_proposals'] = active_proposals

        elif not active_proposals.exists():
            context['active_proposals'] = None

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
        search_query = request.GET.get("search" , "")
        sort_query = request.GET.get("sort" , "")
        if not search_query:
            if sort_query =="":
                creator_accounts = InstagramAccountDashBoard.objects.all().order_by("-date_created")
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

    def form_valid(self, form):
        creator_profile = form.save()
        create_contact = sib_api_v3_sdk.CreateContact(
            email = creator_profile.email,
            update_enabled=True , 
            attributes={
                'FNAME':creator_profile.brand_name,
                'LNAME':" "
            },
            list_ids=[6]
        )
        
        try:
            api_response = api_instance.create_contact(create_contact)
        except sib_api_v3_sdk.ApiException as e:
            print(f"ERROR: {e}")
            messages.add_message(self.request , messages.ERROR , e)
            return self.render_to_response(self.get_context_data(form = form))
        else:
            return super().form_valid(form)

class BrandProfileUpdate(LoginRequiredMixin , UpdateView):
    model = BrandProfile
    fields = ['brand_name' , 'email' , 'about']
    template_name = "base/update_profile.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        profile = form.save()
        create_contact = sib_api_v3_sdk.CreateContact(
            email = profile.email,
            update_enabled=True , 
            attributes={
                'FNAME':profile.brand_name,
                'LNAME':" "
            },

            list_ids=[5]
        )
        
        try:
            api_response = api_instance.create_contact(create_contact)
        except sib_api_v3_sdk.ApiException as e:
            messages.add_message(self.request , messages.ERROR , e)
            return self.render_to_response(self.get_context_data(form = form))
        else:
            return super().form_valid(form)

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
        formatted_tags = form.cleaned_data['tags'].replace("#" , " #")
        dashboard, created = InstagramAccountDashBoard.objects.get_or_create(
            creator = creator,
            tags = formatted_tags,
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

    def form_valid(self, form):
        dashboard = form.save(commit=False)
        dashboard.tags = dashboard.tags.replace("#" , " #")
        dashboard.average_rate = ((dashboard.story_rates + dashboard.reel_rates) // 2)
        dashboard.save()
        return super().form_valid(form)



    def get_success_url(self):
        id = self.kwargs.get('pk')
        return reverse("integration_dashboard" , kwargs= {"pk": id})
    
    
def creator_proposal_view(request , pk):
    proposal = get_object_or_404(BrandProposal , id = pk )
    context = {
        'proposal' : proposal
    }

    return render(request , 'base/creator_proposal_view.html' , context)





def get_brand_proposals(request, brand_id):
    brand = get_object_or_404(BrandProfile , id = brand_id)
    proposals = BrandProposal.objects.filter(brand = brand , proposal_status = BrandProposal.Proposal_Status.REQUESTED)
    accepted_proposals = BrandProposal.objects.filter(brand =  brand , proposal_status = BrandProposal.Proposal_Status.ACCEPTED)
    paid_proposals = BrandProposal.objects.filter(brand =  brand , proposal_status = BrandProposal.Proposal_Status.PAID)

    context = {
        'account':brand,
        'proposals': proposals,
        'accepted_proposals' : accepted_proposals,
        'paid_proposals' : paid_proposals
    }
    return render(request, 'base/brand_proposals.html', context)

class CreateBrandProposal(LoginRequiredMixin , FormView):
    form_class = BrandProposalForm
    template_name = "base/create_proposal.html"
    success_url = reverse_lazy("home")


    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        creator = get_object_or_404(CreatorProfile , id = self.kwargs.get('creator_id'))
        ig_account = get_object_or_404(InstagramAccountDashBoard , creator = creator)
        proposal, created = BrandProposal.objects.get_or_create(
            brand = brand,
            creator = creator,
            account = ig_account,
            
            description = form.cleaned_data['description'],
            timeline = form.cleaned_data['timeline'],
            proposed_amount = form.cleaned_data['proposed_amount'],
            item_link = form.cleaned_data['item_link'],
            content_type = form.cleaned_data['content_type'],
            proposal_status = BrandProposal.Proposal_Status.REQUESTED

            )
        
        return super().form_valid(form)

def accept_brand_proposal(request , proposal_id):
    proposal = get_object_or_404(BrandProposal , id = proposal_id)
    proposal.proposal_status = BrandProposal.Proposal_Status.ACCEPTED
    proposal.save()

    return redirect(reverse_lazy("home"))

def reject_brand_proposal(request , proposal_id):
    proposal = get_object_or_404(BrandProposal , id = proposal_id)
    proposal.proposal_status = BrandProposal.Proposal_Status.REJECTED
    proposal.save()

    return redirect(reverse_lazy("home"))

def creator_active_proposals(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    active_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    context = {
        "account":creator
    }
    
    if active_proposals.exists():
        context['active_proposals'] = active_proposals
        for proposal in active_proposals :
                proposed_date = proposal.date_paid + datetime.timedelta(days = proposal.timeline)
                proposal.duration_left = proposed_date - timezone.now()
                proposal.save()
    else:
        context['active_proposals'] = None

    return render(request , 'base/creator_active_proposals.html' , context)

def creator_payment_dashboard(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    paid_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    pending_payment = decimal.Decimal("0.00")
    for proposal in paid_proposals:
        pending_payment += proposal.proposed_amount
    context = {
        'pending_payment' : pending_payment,
        'paid_proposals' : paid_proposals,
        'account':creator
    }

    return render(request , 'base/creator_payment_dashboard.html' , context)

def brand_proposal_payment(request , proposal_id):
    proposal = get_object_or_404(BrandProposal , id = proposal_id)

    paypal_dict = {
        'business': 'wearaiofficial@gmail.com',
        'amount': proposal.proposed_amount,
        'currency_code':'USD',
        'item_name': "Branded Content Promotion" ,
        'return': request.build_absolute_uri(reverse("successfull_payment" , kwargs={"proposal_id": proposal.id})), #change this
        'cancel_return':request.build_absolute_uri(reverse("payment_failed" , kwargs={"brand_id":proposal.brand.id})) #change this 
    }

    form = PayPalPaymentsForm(initial = paypal_dict)
    context = {
        'proposal':proposal,
        'form': form
    }

    return render(request , "base/brand_proposal_payment.html" ,context)


def successfull_payment(request , proposal_id):
    proposal = get_object_or_404(BrandProposal , id= proposal_id)
    
    proposal.proposal_status = BrandProposal.Proposal_Status.PAID
    proposal.date_paid = timezone.now()
    proposal.save()
    
    return render(request , 'base/successfull_payment.html')

def payment_failed(request , brand_id):
    
    context = {
        'brand_id':brand_id
    }
    
    return render(request , 'base/payment_failed.html', context)

