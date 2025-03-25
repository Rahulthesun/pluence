import urllib.parse , os , hashlib , json
from django.forms import BaseModelForm
from django.http.response import HttpResponseRedirect , HttpResponseForbidden
from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse_lazy , reverse
from django.http import HttpResponse , Http404 , JsonResponse

from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Q


from users.forms import EmailUserCreationForm
from .forms import AccountTypeForm , AccountIntegrationForm , BrandProposalForm ,TiktokBrandProposalForm, DashboardImageForm , EmailVerificationForm , BrandSubscriptionForm
from users.models import EmailUser
from .models import CreatorProfile ,BrandProfile , BrandDeal , InstagramAccountDashBoard , Content_Approval_Media , VerifyEmail,Referral , TiktokDashboard 
from .models import UnsentEmails


from django.contrib.auth.mixins import UserPassesTestMixin , LoginRequiredMixin
from django.contrib.auth import login , authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView , FormView , UpdateView
from django.contrib.auth.views import LoginView , LogoutView
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied 

import requests , datetime , decimal , base64 , urllib
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pluence.settings import TIKTOK_CLIENT_KEY , TIKTOK_CLIENT_SECRET , FERNET_KEY

from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string

'''
EMAIL SENDING CODE W BREVO API

        template_id = 12
        to = [{"email": self.email}]
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
            params={
                'code': self.verification_code
            }
        )

        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email) -> This is the email sending part
            print("API Response:", api_response)
        except ApiException as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
        else:       
            Whatever functionality
'''

imgbb_key = '4293ead9e871a798ed6d0580bb00f15c'
imgbb_url = 'https://api.imgbb.com/1/upload'

payload = {
            'key': imgbb_key
        }


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'
api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

fernet = Fernet(FERNET_KEY) # fernet instance to encrypt/decrypt data 

'''
INSTAGRAM GRAPH API & FACEBOOK AUTH

code = ""
client_id = '2221760501509247'
client_secret = '5fa1b8b40763fa9c9a0d699af2ca19d2'
token_exchange_url = 'https://api.instagram.com/oauth/access_token'
instagram_auth_url = 'https://api.instagram.com/oauth/authorize'
scope = 'instagram_basic,instagram_manage_insights'
response_type = 'code'

'''

#UTILITY FUNCTIONS

#functions for code_verifer & code_challenge for tiktok api
def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip("=")

# Create a code challenge by hashing the verifier with SHA-256 and encoding in base64
def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip("=")


#function for encryting & decryption of sensitive tokens.
def hash_token(token:str)->str: #:str says token should be of str , and ->str means the function gives str value
    return fernet.encrypt(token.encode()).decode()

def unhash_token(hashed_token:str) ->str:
    return fernet.decrypt(hashed_token.encode()).decode()


#testing new landing pages

def new_home(request):
    return render(request , 'base/landing_home.html')



# Create your views here.

def landing_page(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("home"))
    else:
        return render(request ,'base/landing_home.html')


def landing_page_creator(request):
    return render(request , 'base/landing_creator.html')

def landing_page_pricing(request):
    return render(request , 'base/landing_pricing.html')

def privacy_policy(request):
    return render(request, 'base/privacypolicy.html')

def terms_and_conditions(request):
    return render(request, 'base/termsandconditions.html')

#demo view (for brand demo experience)
def brand_demo_home(request , slug=None):
    context = {}
    if slug is None or slug=="instagram":
            social_media = "instagram"
            search_query = request.GET.get("search" , "")
            sort_query = request.GET.get("sort" , "")
            creator1 , creator2 , creator3 , creator4 , creator5 , creator6 = [None] * 6
            instagram_dashboards = [
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard1.png",
                    creator=creator1,
                    username="creator_one",
                    tags="fashion, travel",
                    followers=10000,
                    reach=8000,
                    profile_link_clicks=200,
                    engagement=1200,
                    engagement_rate=15.0,
                    audience_country="United States",
                    story_rates=500.00,
                    reel_rates=800.00,
                    average_rate=650.00,
                    date_created=timezone.now() - datetime.timedelta(days=1)
                ),
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard2.png",
                    creator=creator2,
                    username="creator_two",
                    tags="tech, gadgets",
                    followers=20000,
                    reach=15000,
                    profile_link_clicks=500,
                    engagement=3000,
                    engagement_rate=20.0,
                    audience_country="India",
                    story_rates=700.00,
                    reel_rates=1000.00,
                    average_rate=850.00,
                    date_created=timezone.now() - datetime.timedelta(days=2)
                ),
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard3.png",
                    creator=creator3,
                    username="creator_three",
                    tags="fitness, health",
                    followers=15000,
                    reach=12000,
                    profile_link_clicks=300,
                    engagement=1800,
                    engagement_rate=12.0,
                    audience_country="Canada",
                    story_rates=600.00,
                    reel_rates=900.00,
                    average_rate=750.00,
                    date_created=timezone.now()
                ),
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard4.png",
                    creator=creator4,
                    username="creator_four",
                    tags="beauty, skincare",
                    followers=18000,
                    reach=14000,
                    profile_link_clicks=350,
                    engagement=2000,
                    engagement_rate=11.1,
                    audience_country="United Kingdom",
                    story_rates=550.00,
                    reel_rates=850.00,
                    average_rate=700.00,
                    date_created=timezone.now() - datetime.timedelta(days=3)
                ),
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard5.png",
                    creator=creator5,
                    username="creator_five",
                    tags="food, tech",
                    followers=25000,
                    reach=20000,
                    profile_link_clicks=600,
                    engagement=3500,
                    engagement_rate=14.0,
                    audience_country="Australia",
                    story_rates=750.00,
                    reel_rates=1100.00,
                    average_rate=925.00,
                    date_created=timezone.now() - datetime.timedelta(days=4)
                ),
                InstagramAccountDashBoard(
                    dashboard_img="https://example.com/dashboard6.png",
                    creator=creator6,
                    username="creator_six",
                    tags="travel, adventure,recipes",
                    followers=30000,
                    reach=25000,
                    profile_link_clicks=700,
                    engagement=4000,
                    engagement_rate=16.0,
                    audience_country="Germany",
                    story_rates=800.00,
                    reel_rates=1200.00,
                    average_rate=1000.00,
                    date_created=timezone.now() - datetime.timedelta(days=5)
                )
            ]           
            if not search_query:
                if sort_query =="":
                    creator_accounts = sorted(instagram_dashboards , key = lambda d: d.date_created , reverse=True)
                elif sort_query == "followers-asc" :
                    creator_accounts = sorted(instagram_dashboards , key = lambda d: d.followers , reverse=False)
                else:
                    creator_accounts = sorted(instagram_dashboards , key = lambda d: d.followers , reverse=True)

            elif search_query:
                searched_instagram_dashboards = list(filter(lambda dashboard: search_query.lower() in dashboard.tags.lower() , instagram_dashboards))
                if sort_query == "":
                    creator_accounts = sorted(searched_instagram_dashboards , key = lambda d: d.date_created , reverse=True)
                if sort_query == 'followers-asc':
                    creator_accounts = sorted(searched_instagram_dashboards , key = lambda d: d.followers , reverse=False)
                else:
                    creator_accounts = sorted(searched_instagram_dashboards , key = lambda d: d.followers , reverse=True)
            #testing out brand account dynamic navbar 

            context['social_media'] = social_media
            context['creators'] = creator_accounts
    elif slug == "tiktok":
        social_media = "tiktok"
        search_query = request.GET.get("search" , "")
        sort_query = request.GET.get("sort" , "")
        creator1 , creator2 , creator3 , creator4 , creator5 , creator6 = [None] * 6
        tiktok_dashboards = [
            TiktokDashboard(
                creator=creator1,
                access_token="example_access_token_1",
                refresh_token="example_refresh_token_1",
                avatar_url="https://i1.sndcdn.com/artworks-rt0SRHC7TbqoV1vz-TpU0sw-t500x500.jpg",
                open_id="open_id_1",
                display_name="creator_one",
                profile_deep_link="https://tiktok.com/@creator_one",
                is_verified=True,
                follower_count=50000,
                likes_count=250000,
                video_count=300,
                engagement_rate=decimal.Decimal('15.0'),
                deal_count=10,
                tags="beauty, fashion",
                pricing_per_promotion=decimal.Decimal('1000.00'),
                created=timezone.now() - datetime.timedelta(days=1)
            ),
            TiktokDashboard(
                creator=creator2,
                access_token="example_access_token_2",
                refresh_token="example_refresh_token_2",
                avatar_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDZg9g8y-0ZEuouxoqwc5vNvPzx5no2s9mhw&s",
                open_id="open_id_2",
                display_name="creator_two",
                profile_deep_link="https://tiktok.com/@creator_two",
                is_verified=False,
                follower_count=30000,
                likes_count=150000,
                video_count=200,
                engagement_rate=decimal.Decimal('12.0'),
                deal_count=5,
                tags="tech, gadgets,techtok,new,apple",
                pricing_per_promotion=decimal.Decimal('800.00'),
                created=timezone.now() - datetime.timedelta(days=2)
            ),
            TiktokDashboard(
                creator=creator3,
                access_token="example_access_token_3",
                refresh_token="example_refresh_token_3",
                avatar_url="https://i1.sndcdn.com/artworks-nkVzxkkJNjLVDWQc-fYrUHw-t500x500.jpg",
                open_id="open_id_3",
                display_name="creator_three",
                profile_deep_link="https://tiktok.com/@creator_three",
                is_verified=True,
                follower_count=70000,
                likes_count=400000,
                video_count=500,
                engagement_rate=decimal.Decimal('20.0'),
                deal_count=15,
                tags="fitness, health, food",
                pricing_per_promotion=decimal.Decimal('1500.00'),
                created=timezone.now()
            ),
            TiktokDashboard(
                creator=creator4,
                access_token="example_access_token_4",
                refresh_token="example_refresh_token_4",
                avatar_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqB1tMiBMaCr3D44TRQ5iVQuBhBwdmfQnrMw&s",
                open_id="open_id_4",
                display_name="creator_four",
                profile_deep_link="https://tiktok.com/@creator_four",
                is_verified=False,
                follower_count=45000,
                likes_count=220000,
                video_count=250,
                engagement_rate=decimal.Decimal('10.5'),
                deal_count=8,
                tags="travel, adventure, wanderlust,tech",
                pricing_per_promotion=decimal.Decimal('950.00'),
                created=timezone.now() - datetime.timedelta(days=3)
            ),
            TiktokDashboard(
                creator=creator5,
                access_token="example_access_token_5",
                refresh_token="example_refresh_token_5",
                avatar_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSL0Yl9xq7Bp89j-yw21WbqpiI5yPdShUBo5hiz5VsluHMD6uZWES6xJYsJZU1tTNF43b8&usqp=CAU",
                open_id="open_id_5",
                display_name="creator_five",
                profile_deep_link="https://tiktok.com/@creator_five",
                is_verified=True,
                follower_count=60000,
                likes_count=350000,
                video_count=400,
                engagement_rate=decimal.Decimal('17.0'),
                deal_count=12,
                tags="food, recipes, cooking ,learning",
                pricing_per_promotion=decimal.Decimal('1200.00'),
                created=timezone.now() - datetime.timedelta(days=4)
            ),
            TiktokDashboard(
                creator=creator6,
                access_token="example_access_token_6",
                refresh_token="example_refresh_token_6",
                avatar_url="https://i.pinimg.com/236x/7f/5a/93/7f5a93164763d62faec8fa300dc28b7e.jpg",
                open_id="open_id_6",
                display_name="creator_six",
                profile_deep_link="https://tiktok.com/@creator_six",
                is_verified=False,
                follower_count=25000,
                likes_count=120000,
                video_count=150,
                engagement_rate=decimal.Decimal('8.0'),
                deal_count=4,
                tags="education, edutok, learning,travel",
                pricing_per_promotion=decimal.Decimal('700.00'),
                created=timezone.now() - datetime.timedelta(days=5)
            )
        ]
        if not search_query:
            if sort_query =="":
                creator_accounts = sorted(tiktok_dashboards , key = lambda d: d.created , reverse=True)
            elif sort_query == "followers-asc" :
                creator_accounts = sorted(tiktok_dashboards , key = lambda d: d.follower_count , reverse=False)
            else:
                creator_accounts = sorted(tiktok_dashboards , key = lambda d: d.follower_count , reverse=True)
        elif search_query:
            searched_tiktok_dashboards = list(filter(lambda dashboard: search_query.upper() in dashboard.tags.upper() , tiktok_dashboards))
            if sort_query == "":
                creator_accounts = sorted(searched_tiktok_dashboards , key = lambda d: d.created , reverse=True)
            if sort_query == 'followers-asc':
                creator_accounts = sorted(searched_tiktok_dashboards , key = lambda d: d.follower_count , reverse=False)
            else:
                creator_accounts = sorted(searched_tiktok_dashboards , key = lambda d: d.follower_count , reverse=True)
        #testing out brand account dynamic navbar 
        context['social_media'] = social_media
        context['creators'] = creator_accounts

    return render(request , 'base/demo_brand_home.html' , context)

def demo_redirect(request):
    return render(request , 'base/demo_redirect.html')

class CreateDemoProposal(FormView):
    form_class = TiktokBrandProposalForm
    template_name = "base/create_proposal.html"

    def dispatch(self, *args, **kwargs):
        if not self.request.session.get('demo_message_shown'):
            messages.info(self.request, "This is a demo version. No data will be saved.")
            self.request.session['demo_message_shown'] = True  # Mark as shown
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        return redirect(reverse_lazy("demo_redirect"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            messages.get_messages(self.request).used = True
        return context

@login_required
def home(request, slug=None):

    creator_account = CreatorProfile.objects.filter(user = request.user)
    brand_account = BrandProfile.objects.filter(user = request.user)
    context = {}
    if creator_account.exists():
        ig_proposals = BrandDeal.objects.filter(creator = creator_account[0] , proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT , platform = BrandDeal.Platforms.INSTAGRAM)
        tiktok_proposals = BrandDeal.objects.filter(creator = creator_account[0] , proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT , platform = BrandDeal.Platforms.TIKTOK)

        ig_account = InstagramAccountDashBoard.objects.filter(creator = creator_account[0])
        tiktok_account = TiktokDashboard.objects.filter(creator = creator_account[0])
        #change the ig_active_proposals status-es
        
        ig_active_proposals = BrandDeal.objects.filter(
            Q(creator = creator_account[0]) & Q(platform=BrandDeal.Platforms.INSTAGRAM) & (Q(proposal_status = BrandDeal.Proposal_Status.PROPOSAL_ACCEPTED) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_PAID) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT))
        )

        tiktok_active_proposals = BrandDeal.objects.filter(
            Q(creator = creator_account[0]) & Q(platform=BrandDeal.Platforms.INSTAGRAM) & (Q(proposal_status = BrandDeal.Proposal_Status.PROPOSAL_ACCEPTED) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_PAID) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING) | Q(proposal_status = BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT))
        )


        #referral = Referral.objects.get(referrer = creator_account)
        #context['referral_code'] = referral.code
        links = {}
        if ig_active_proposals.exists() or tiktok_active_proposals.exists():
            #context['ig_active_proposals'] = ig_active_proposals
            links['active_proposals'] = {
            'url': reverse("creator_active_proposals" , kwargs={"creator_id":creator_account[0].id}),
            'name': "Active Deals"
            }

        elif not ig_active_proposals.exists() and not tiktok_active_proposals.exists():
            context['active_proposals'] = None
            
        context['account'] = creator_account[0]  
        context['ig_proposals'] = None
        context['tiktok_proposals'] = None
        context['ig_account'] = None
        context['tiktok_account'] = None

        if ig_proposals.exists():
            context['ig_proposals'] = ig_proposals

        if tiktok_proposals.exists():
            context['tiktok_proposals'] = tiktok_proposals

        if ig_account.exists():
            context['ig_account'] = ig_account[0]

        if tiktok_account.exists():
            context['tiktok_account'] = tiktok_account[0]
           

        if ig_account.exists() or tiktok_account.exists():
            links['manage_integrations'] = {
                    'url': reverse("integration_dashboard" , kwargs={"pk":creator_account[0].id}),
                    'name': "Manage Integrations"
                    }
        links['payment_dashboard'] = {
            'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":creator_account[0].id}),
            'name': "Payment Dashboard"
        }

        links['update_profile'] = {
            'url': reverse("creator_profile_update" , kwargs={"pk":creator_account[0].id}),
            'name': "Update Profile"
        }

        links['referral_link'] = {
            'url': reverse("referral_dashboard" , kwargs={"creator_id":creator_account[0].id}),
            'name': "Referral Dashboard"
        }
       
        context['links'] = links
        context['username']= creator_account[0].name
        template = 'base/creator_home.html'
    elif brand_account.exists():
        if slug is None or slug=="instagram":
            social_media = "instagram"
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
                if sort_query == "":
                    creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query).order_by("-date_created")
                if sort_query == 'followers-asc':
                    creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query).order_by('followers')
                else:
                    creator_accounts = InstagramAccountDashBoard.objects.filter(tags__icontains = search_query).order_by('-followers')
            #testing out brand account dynamic navbar 

            context['social_media'] = social_media
            context['creators'] = creator_accounts

        #creator view for tiktok selection that shows only tiktok dashboards
        elif slug == "tiktok":
            social_media = "tiktok"
            search_query = request.GET.get("search" , "")
            sort_query = request.GET.get("sort" , "")
            if not search_query:
                if sort_query =="":
                    creator_accounts = TiktokDashboard.objects.all().order_by("-created")
                elif sort_query == "followers-asc" :
                    creator_accounts = TiktokDashboard.objects.all().order_by("follower_count")
                else:
                    creator_accounts = TiktokDashboard.objects.all().order_by("-follower_count")

            elif search_query:
                if sort_query == "":
                    creator_accounts = TiktokDashboard.objects.filter(tags__icontains = search_query).order_by("-created")
                if sort_query == 'followers-asc':
                    creator_accounts = TiktokDashboard.objects.filter(tags__icontains = search_query).order_by('follower_count')
                else:
                    creator_accounts = TiktokDashboard.objects.filter(tags__icontains = search_query).order_by('-follower_count')
            
            context['social_media'] = social_media
            context['creators'] = creator_accounts
    
        #The same brand code for both tiktok and ig media because brand proposals and brand account is both same 
        context['account'] = brand_account[0]
        account = brand_account[0]
        if account.brand_name:
            context['username'] = account.brand_name
        context['pending_proposals'] = BrandDeal.objects.filter(brand = account ,proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
        
        your_proposals = BrandDeal.objects.filter(brand = account)
        
        links = {}
        
        #content approval pending link to be added to dynamic navbar links
        if context['pending_proposals'].exists() :
            num = len(context['pending_proposals']) 
            links["content_approval"]= {
                'url' : reverse_lazy("pending_content_approval"),
                'name' : f'Content Approval ({num})'
            }
        #your proposal link added to DN(Dynamic navbar) Links
        if your_proposals.exists() :
            links["your_proposals"] = {
                'url': reverse("brand_proposals" ,kwargs={"brand_id":brand_account[0].id}),
                'name': 'Your Proposals'
            }
        #constant update_profile link
        links['update_profile'] = {
            'url': reverse("brand_profile_update" , kwargs={"pk":account.id}),
            'name': "Update Profile"
        }
        context["links"] = links
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
    
    
    def form_valid(self , form):
        email = form.cleaned_data['email']
        self.email = email
        verification_code = get_random_string(length=6)
        verification , created = VerifyEmail.objects.get_or_create(
            email=email, 
            verification_code=verification_code
        )
        self.verification_id = verification.id
        self.send_verification_email(email, verification_code)

        user = form.save(commit=False)
        user.is_active = False #Disabling user untill verification is created
        user.save()

        '''
        #login(self.request, user)
        '''
        return super().form_valid(form)

    def send_verification_email(self, email, verification_code):
        template_id = 18
        to = [{"email": email}]
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
            params={
                'code': verification_code
            }
        )
        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
        except ApiException as e:
            print(f"Error: {e}")

    def get_success_url(self):
        #hashing email as one of the attributes so it's not visible
        referral_code = self.kwargs.get("referral_code")
        if referral_code:
            return reverse("signup_email_verification_with_referral", kwargs={"pk": hash_token(self.email), "verify_id": self.verification_id , "referral_code" : referral_code})
        else:
            return reverse("signup_email_verification", kwargs={"pk": hash_token(self.email), "verify_id": self.verification_id })

    def test_func(self):
        return self.request.user.is_anonymous
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy("home"))
    
class SignupEmailVerification(FormView):
    template_name = "base/email_verification.html"
    form_class = EmailVerificationForm

    def form_valid(self, form):
        verification_code = form.cleaned_data['verification_code']
        verify_id = self.kwargs.get('verify_id')
        email = unhash_token(self.kwargs.get('pk'))


        verification = get_object_or_404(VerifyEmail, id=verify_id)

        if verification.verification_code == verification_code:
            if verification.verified:
                messages.error(self.request, "This email has already been verified.")
                return self.form_invalid(form)
            verification.verified = True
            verification.save()
            user = get_object_or_404(EmailUser , email = verification.email)
            user.is_active = True
            user.save()
            login(self.request, user)
            verification.user = self.request.user
            verification.save()
            referral_code = self.kwargs.get("referral_code")
            if referral_code:
                print(referral_code)
                 #MATCHING THE REFERRAL CODE OF THE USER TO THE REFERRAL CODE OF ALL CREATORS
                try:
                    referrer_creator = CreatorProfile.objects.get(referral_link_code=referral_code)
                except CreatorProfile.DoesNotExist:
                    messages.error(self.request, "Invalid referral code. Normal signup completed.")
                else:
                    referrer_creator.referral_balance += decimal.Decimal(1)
                    referrer_creator.referral_link_used += 1
                    referrer_creator.save()
                    messages.success(self.request, "Referral code processed successfully.")
            else:
                print("No REFERRAL CODE IS GIVEN")
            return redirect(reverse_lazy('account_selection'))
        else:
            form.add_error('verification_code', 'Invalid verification code.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.GET.get('email')  # Pass the email to the template
        return context

    

class AccountType(UserPassesTestMixin ,FormView,LoginRequiredMixin):
    form_class = AccountTypeForm
    template_name = "base/account_selection.html"
    
    def test_func(self):
        # trying to prevent non logged in users from reaching this page
        if not self.request.user.is_authenticated:
            return False
        creator_account = CreatorProfile.objects.filter(user = self.request.user)
        brand_account = BrandProfile.objects.filter(user = self.request.user)
        if brand_account.exists() or creator_account.exists() :
            return False
        else:
            return True
        
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy("home"))

    def form_valid(self, form):
        self.brand_account = False
        account_type = form.cleaned_data['account_type']
        if account_type == "brand":
            self.brand_account = True
            account,created = BrandProfile.objects.get_or_create(user = self.request.user , email = self.request.user.email)
            verification = get_object_or_404(VerifyEmail , email = self.request.user.email)
            verification.account_type = VerifyEmail.AccountType.BRAND
        else:
            account,created = CreatorProfile.objects.get_or_create(user = self.request.user, contact_email =self.request.user.email)
            verification = get_object_or_404(VerifyEmail , email = self.request.user.email)
            verification.account_type = VerifyEmail.AccountType.CREATOR
            
        account.save()
        verification.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("home")
    

class BrandAccountSubscription(UserPassesTestMixin ,LoginRequiredMixin ,FormView):
    template_name = 'base/brand_subscription.html'
    form_class = BrandSubscriptionForm

    def test_func(self):

        brand = get_object_or_404(BrandProfile, id=self.kwargs.get("brand_id"))
        return brand.user == self.request.user

    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile, id=self.kwargs.get('brand_id'))
        brand.subscription_months = int(form.cleaned_data['months'])
        brand.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("brand_subscription_payment", kwargs={"brand_id": self.kwargs.get('brand_id')})

@login_required 
def brand_subscription_payment(request , brand_id):
    brand = get_object_or_404(BrandProfile , id = brand_id)
    if brand.user != request.user:
        raise PermissionDenied
    
    subscription_amount = 5 * brand.subscription_months
    
    paypal_dict = {
        'business': 'wearaiofficial@gmail.com',
        'amount': subscription_amount,
        'currency_code':'USD',
        'item_name': f"Pluence Brand Subscription {brand.subscription_months} months" ,
        'return': request.build_absolute_uri(reverse("brand_subscription_activation" , kwargs={"brand_id": brand.id})), 
        'cancel_return':request.build_absolute_uri(reverse("payment_failed" , kwargs={"brand_id":brand.id}))  
    }

    form = PayPalPaymentsForm(initial = paypal_dict)
    
    context = {
        'amount': subscription_amount,
        'form': form
    }

    return render(request , "base/brand_subscription_payment.html" , context) 

@login_required
def brand_subscription_activation(request , brand_id):
    brand = get_object_or_404(BrandProfile , id = brand_id)

    brand.subscription_active = True
    brand.subscribed_date = timezone.now()
    brand.subscription_expiry_date = brand.subscribed_date + datetime.timedelta(days=(brand.subscription_months*31))
    brand.subscription_expiry_duration = brand.subscription_expiry_date - brand.subscribed_date
    brand.save()

    return render(request , 'base/successfull_payment.html' , context = {})

class CreatorProfileUpdate(UserPassesTestMixin , LoginRequiredMixin , UpdateView):
    model = CreatorProfile
    fields = ['name' , 'bio' ,'contact_email' , 'website' ]
    template_name = "base/update_profile.html"

    
    def test_func(self):
        creator = get_object_or_404(CreatorProfile , id=self.kwargs.get("pk"))
        return creator.user==self.request.user
    
    #Sends user to verify_email first and then adds email to contact , and updates creator_profile
    def form_valid(self, form):
        creator_profile = form.save(commit=False)
        verification , created = VerifyEmail.objects.get_or_create(
            #user = self.request.user ,
            email = creator_profile.contact_email,
            account_type = VerifyEmail.AccountType.CREATOR
        )

        #IF A VERIFYEMAIL INSTANCE EXISTS WITH SAME EMAIL ENTERED AS INPUT FOR CREATOR ACCOUNTS , 
        #THEN IT IS CHECKED IF IT'S THE SAME USER , OR ELSE IT SHOWS ERROR 'EMAIL ALREADY EXISTS'
        #IF VERIFIED IS FALSE , IT'S SENT FOR VERIFICATION
        #IF VERIFYEMAIL DOES NOT EXIST , IT CREATES A VERIFYEMAIL INSTANCE W EMAIL FOR CREATOR ACCOUNTS  AND VERIFIES IT  

        if created == False:
            if verification.user == self.request.user:
                if verification.verified == True:
                    form.save(commit=True)
                    self.verify_id = None
                else:
                    creator_profile.contact_email = None
                    creator_profile.save()
                    verification.generate_verification_code()
                    self.verify_id = verification.id

                    #sending Verification email using send_verification_email() method defined in the VerifyEmail Model's methods
                    if verification.verification_code:
                        email_sent = verification.send_verification_email()
                        if email_sent == False:
                            messages.add_message(self.request, messages.ERROR, f"An unexpected error occurred , Try Again Sometime Later")
                            return redirect(reverse_lazy("home"))
            else:
                form.add_error('contact_email' , "Email Already Exists! Use Another Email")
                return self.form_invalid(form)
        
        elif created == True:
            creator_profile.contact_email = None
            creator_profile.save()
            verification.generate_verification_code()
            self.verify_id = verification.id
     #sending Verification email using send_verification_email() method defined in the VerifyEmail Model's methods
            if verification.verification_code:
                #SETTING VERIFYEMAIL INSTANCE TO SPECIFIC USER
                verification.user = self.request.user
                verification.save()
                email_sent = verification.send_verification_email()
                if email_sent == False:
                    messages.add_message(self.request, messages.ERROR, f"An unexpected error occurred , Try Again Sometime Later")
                    return redirect(reverse_lazy("home"))


        
        return super().form_valid(form)

            
        
    # sends creator user to verify email 
    def get_success_url(self):
        if self.verify_id == None :
            return reverse_lazy("home")
        else:
            return reverse("email_verification" , kwargs={"pk":self.kwargs.get("pk") , "verify_id": self.verify_id})
        
#similiar to CreatorProfileUpdate but with different fields and BrandProfile
class BrandProfileUpdate(UserPassesTestMixin , LoginRequiredMixin , UpdateView):
    model = BrandProfile
    fields = ['brand_name' , 'email' , 'about']
    template_name = "base/update_profile.html"

    def test_func(self):
        brand= get_object_or_404(BrandProfile , id=self.kwargs.get("pk"))
        return brand.user==self.request.user

    def form_valid(self, form):
        brand_profile = form.save(commit=False)
        #the account type and email fields change

        verification , created = VerifyEmail.objects.get_or_create(
            email =brand_profile.email,
            account_type = VerifyEmail.AccountType.BRAND
        )


        if created == False:
            if verification.user == self.request.user:
                if verification.verified == True:
                    form.save(commit=True)
                    self.verify_id = None
                else:
                    brand_profile.email = None
                    brand_profile.save()
                    verification.generate_verification_code()
                    self.verify_id = verification.id

                    #sending Verification email using send_verification_email() method defined in the VerifyEmail Model's methods
                    if verification.verification_code:
                        email_sent = verification.send_verification_email()
                        if email_sent == False:
                            messages.add_message(self.request, messages.ERROR, f"An unexpected error occurred , Try Again Sometime Later")
                            return redirect(reverse_lazy("home"))
            else:
                form.add_error('email' , "Email Already Exists! Use Another Email")
                return self.form_invalid(form)
        
        elif created == True:
            brand_profile.email = None
            brand_profile.save()
            verification.generate_verification_code()
            self.verify_id = verification.id
     #sending Verification email using send_verification_email() method defined in the VerifyEmail Model's methods
            if verification.verification_code:
                #SETTING VERIFYEMAIL INSTANCE TO SPECIFIC USER
                verification.user = self.request.user
                verification.save()
                email_sent = verification.send_verification_email()
                if email_sent == False:
                    messages.add_message(self.request, messages.ERROR, f"An unexpected error occurred , Try Again Sometime Later")
                    return redirect(reverse_lazy("home"))


        
        return super().form_valid(form)
    
        
    # sends brand user to verify email 
    def get_success_url(self):
        if self.verify_id == None:
            return reverse_lazy("home")
        else:
            return reverse("email_verification" , kwargs={"pk":self.kwargs.get("pk") , "verify_id": self.verify_id})

class EmailVerification(UserPassesTestMixin , LoginRequiredMixin , FormView):
    form_class = EmailVerificationForm
    template_name = "base/email_verification.html"



    def test_func(self):
        verification = get_object_or_404(VerifyEmail, id=self.kwargs.get("verify_id"))
        if (verification.user != self.request.user):
            return False  # Return False if creator not found
        return True


    def form_valid(self, form):
        email_list_id = []
        email_code = form.cleaned_data['verification_code']
        verification = get_object_or_404(VerifyEmail , id = self.kwargs.get("verify_id"))
        if email_code == verification.verification_code:
            if verification.account_type == VerifyEmail.AccountType.CREATOR:
                profile = get_object_or_404(CreatorProfile , id=self.kwargs.get("pk"))
                profile.contact_email = verification.email #profile object is being saved below
                email_list_id.append(6)
                create_contact = sib_api_v3_sdk.CreateContact(
                    email = verification.email,
                    update_enabled=True , 
                    attributes={
                        "FIRSTNAME": profile.name,
                    },
                    list_ids=email_list_id
                )   

            elif verification.account_type == VerifyEmail.AccountType.BRAND:
                profile = get_object_or_404(BrandProfile , id=self.kwargs.get("pk"))
                profile.email = verification.email 
                email_list_id.append(5)
                create_contact = sib_api_v3_sdk.CreateContact(
                    email = verification.email,
                    update_enabled=True , 
                    attributes={
                        "FIRSTNAME": profile.brand_name,
                    },
                    list_ids=email_list_id
                )   
   
            

            try:
                print(f"Attributes being sent: {create_contact.attributes}")
                print("Contact being added")
                api_response = api_instance.create_contact(create_contact)
                print(f"API Response: {api_response}")
            except ApiException as e:
                print("API ERROR{e}")
                #messages.add_message(self.request , messages.ERROR , f"{e} Error : Try Again")
                form.add_error('email_code' ,  f"{e} Error : Try Again" )
                return self.form_invalid(form)
            else:
                print("SUCCESSFULL")
                verification.verified = True
                profile.save()
                verification.save()
                return super().form_valid(form)
        else:
            print(f"Code Incorrect")
            #messages.add_message(self.request , messages.ERROR , "Verification code is Incorrect!! Try Again")
            form.add_error('email_code' , "Verification code is Incorrect!! Try Again")
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        # Return the invalid form (with errors) to the template
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy("home")

@login_required
def integration_dashboard(request , pk):
        creator_profile = get_object_or_404(CreatorProfile , id=pk)
        if request.user != creator_profile.user :
            raise PermissionDenied
        ig_dashboards = InstagramAccountDashBoard.objects.filter(creator= creator_profile)
        tiktok_dashboards = TiktokDashboard.objects.filter(creator=creator_profile)

        context = {}

        if not ig_dashboards.exists() :
            ig_dashboard = None
        else:
            ig_dashboard = ig_dashboards[0]
        if not tiktok_dashboards.exists():
            tiktok_dashboard = None
        else:
            tiktok_dashboard = tiktok_dashboards[0]
        links={}
        active_proposals = BrandDeal.objects.filter(creator=creator_profile , proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE)
        if active_proposals.exists():
            links['active_proposals'] = {
                'url': reverse("creator_active_proposals" , kwargs={"creator_id":creator_profile.id}),
                'name': "Active Proposals"
            }
        links['payment_dashboard'] = {
                'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":creator_profile.id}),
                'name': "Payment Dashboard"
            }

        context = {
            'ig_dashboard': ig_dashboard,
            'tiktok_dashboard': tiktok_dashboard,
            "links": links,
            'username': creator_profile.name
        }
        return render(request , 'base/integration_dashboard.html' , context)


class AccountIntegration(LoginRequiredMixin ,FormView):
    form_class = AccountIntegrationForm
    template_name = 'base/account_integration.html'
    success_url = reverse_lazy("home")
    

    def form_valid(self, form):
        creator = get_object_or_404(CreatorProfile ,user = self.request.user)
        
        
        #ENGAGEMENT RATE FORMULA : (New Engagement Rate Formula adjusted & normalized for higher denominator)
        engagement_rate = decimal.Decimal((form.cleaned_data['engagement'] / (form.cleaned_data['engagement'] + form.cleaned_data['followers']))*100)
        avg_rate = round((form.cleaned_data['engagement']/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(form.cleaned_data['followers']) ** decimal.Decimal(1)))
        if avg_rate < 5 :
            avg_rate = 5

        lower_bound = round((form.cleaned_data['engagement']/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(form.cleaned_data['followers']) ** decimal.Decimal(0.95)))
        upper_bound = round((form.cleaned_data['engagement']/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(form.cleaned_data['followers']) ** decimal.Decimal(1.05)))

        if avg_rate < 5:
            avg_rate = 5
            dashboard.average_rate = avg_rate
        if avg_rate < lower_bound :
            form.add_error("average_rate" , f"You're Pricing is Too low . Ideal Pricing For you is ${lower_bound} - ${upper_bound}")
            return self.form_invalid(form)
        if avg_rate > upper_bound :
            form.add_error("average_rate" , f"You're Pricing is Too High . Ideal Pricing For you is ${lower_bound} - ${upper_bound}")
            return self.form_invalid(form)
        # 1 = Follower Factor , 0.02 = Base Rate 

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
            average_rate = avg_rate,
            engagement_rate = engagement_rate
            )
        self.id = dashboard.id
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse("integration_dashboard" , kwargs= {"pk": self.id})
    
class AccountIntegrationUpdate(UserPassesTestMixin ,LoginRequiredMixin , UpdateView):
    model = InstagramAccountDashBoard
    form_class = AccountIntegrationForm
    template_name = 'base/account_integration.html'

    def test_func(self):
        dashboard = get_object_or_404(InstagramAccountDashBoard , id = self.kwargs.get("pk"))
        return dashboard.creator.user == self.request.user

    def form_valid(self, form):
        dashboard = form.save(commit=False)
        dashboard.tags = dashboard.tags.replace("#" , " #")
        dashboard.engagement_rate = decimal.Decimal((dashboard.engagement / (dashboard.engagement + dashboard.followers) )*100)
        dashboard.save()
        avg_rate = round((dashboard.engagement_rate/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(dashboard.followers) ** decimal.Decimal(1)))#(form.cleaned_data['story_rates'] + form.cleaned_data['reel_rates']) // 2
        
        lower_bound = round((dashboard.engagement_rate/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(dashboard.followers) ** decimal.Decimal(0.95)))
        upper_bound = round((dashboard.engagement_rate/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(dashboard.followers) ** decimal.Decimal(1.05)))

        if avg_rate < 5:
            avg_rate = 5
            dashboard.average_rate = avg_rate
        if dashboard.average_rate < lower_bound :
            form.add_error("average_rate" , f"You're Pricing is Too low . Ideal Pricing For you is ${lower_bound} - ${upper_bound}")
            return self.form_invalid(form)
        if dashboard.average_rate > upper_bound :
            form.add_error("average_rate" , f"You're Pricing is Too High . Ideal Pricing For you is ${lower_bound} - ${upper_bound}")
            return self.form_invalid(form)
        
        print(avg_rate)
        dashboard.save()
        return super().form_valid(form)

    def get_success_url(self):
        id = self.kwargs.get('pk')
        return reverse("integration_dashboard" , kwargs= {"pk": id})
    
class DashboardImageUpdate(UserPassesTestMixin,LoginRequiredMixin , FormView):
    form_class = DashboardImageForm
    template_name = 'base/dashboard_img_form.html'

    def test_func(self):
        dashboard = get_object_or_404(InstagramAccountDashBoard , id=self.kwargs.get("pk"))
        return dashboard.creator.user == self.request.user

    def form_valid(self, form):
        account = get_object_or_404(InstagramAccountDashBoard , id = self.kwargs.get('pk'))
        img = form.cleaned_data['dashboard_img'].read()
        payload['image'] = base64.b64encode(img).decode('utf-8')
        response = requests.post(imgbb_url, data=payload)
        print(f"Response status code: {response.status_code}")
        
        json_response = response.json()

        if response.status_code == 200:
            img_url = json_response['data']['url']
            account.dashboard_img = img_url
            account.save()
            return super().form_valid(form)
            
        else:
            print("Error uploading image to imgbb:", json_response)
            messages.add_message(self.request, messages.ERROR, "Error uploading image to Server")

    def get_success_url(self):
        id = self.kwargs.get('pk')
        return reverse("integration_dashboard" , kwargs= {"pk": id})

@login_required    
def brand_proposal_view(request , pk):
    proposal = get_object_or_404(BrandDeal , id=pk)
    if proposal.brand.user != request.user:
        raise PermissionDenied
    links = {}
    pending_proposals = BrandDeal.objects.filter(brand = proposal.brand , proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    if pending_proposals.exists():
        links["content_approval"]= {
                'url' : reverse_lazy("pending_content_approval"),
                'name' : f'Content Approval ({len(pending_proposals)})'
            }
    links['your_proposals'] = {
            "url" : reverse("brand_proposals" , kwargs={"brand_id": proposal.brand.id}),
            "name": "Your Proposals"
        } 
    
    context = {
        "proposal": proposal,
        "links": links
    }

    return render(request , 'base/brand_proposal_view.html' , context)

@login_required
def creator_proposal_view(request , pk):
    proposal = get_object_or_404(BrandDeal , id = pk)
    #restrict other users from using link
    if proposal.creator.user != request.user :
            raise PermissionDenied
    links={}
    active_proposals = BrandDeal.objects.filter(creator=proposal.creator , proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE)
    if active_proposals.exists() :
        links['active_proposals'] = {
                'url': reverse("creator_active_proposals" , kwargs={"creator_id":proposal.creator.id}),
                'name': "Active Proposals"
        }
    ig_dashboard = InstagramAccountDashBoard.objects.filter(creator = proposal.creator)
    tiktok_dashboard = TiktokDashboard.objects.filter(creator = proposal.creator)
    if ig_dashboard.exists() or tiktok_dashboard.exists():
        links['manage_integrations'] = {
                'url': reverse("integration_dashboard" , kwargs={"pk":proposal.creator.id}),
                'name': "Manage Integrations"
                }
    links['payment_dashboard'] = {
            'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":proposal.creator.id}),
            'name': "Payment Dashboard"
            }

    context = {
        'proposal' : proposal,
        "links" : links
    }


    return render(request , 'base/creator_proposal_view.html' , context)




@login_required
def get_brand_proposals(request, brand_id):
    brand = get_object_or_404(BrandProfile , id = brand_id)
    if brand.user != request.user:
        raise PermissionDenied
    
    ig_proposals = BrandDeal.objects.filter(brand = brand , platform = BrandDeal.Platforms.INSTAGRAM , proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT)
    #payment-due is used as accepted proposals i.e. ACCEPTED is a proposals status that is temp while sending emails . DEAL_PAYMENT_DUE IS THE proposals status used to query the proposals - ACCEPTED BUT NOT PAID YET
    ig_accepted_proposals = BrandDeal.objects.filter(brand =  brand , platform = BrandDeal.Platforms.INSTAGRAM , proposal_status = BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE)
    ig_active_proposals = BrandDeal.objects.filter(brand =  brand ,platform = BrandDeal.Platforms.INSTAGRAM , proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE)
    ig_pending_proposals = BrandDeal.objects.filter(brand= brand , platform = BrandDeal.Platforms.INSTAGRAM , proposal_status= BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    ig_posting_proposals = BrandDeal.objects.filter(brand= brand , platform = BrandDeal.Platforms.INSTAGRAM , proposal_status= BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT)

  
    
    tiktok_proposals = BrandDeal.objects.filter(brand = brand , platform = BrandDeal.Platforms.TIKTOK , proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT)
    tiktok_accepted_proposals = BrandDeal.objects.filter(brand =  brand , platform = BrandDeal.Platforms.TIKTOK , proposal_status = BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE)
    tiktok_active_proposals = BrandDeal.objects.filter(brand =  brand ,platform = BrandDeal.Platforms.TIKTOK , proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE)
    tiktok_pending_proposals = BrandDeal.objects.filter(brand= brand , platform = BrandDeal.Platforms.TIKTOK , proposal_status= BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    tiktok_posting_proposals = BrandDeal.objects.filter(brand= brand , platform = BrandDeal.Platforms.TIKTOK , proposal_status= BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT)


    ig_num = len(ig_proposals) + len(ig_accepted_proposals) + len(ig_active_proposals) +  len(ig_pending_proposals) + len(ig_posting_proposals)
    tiktok_num = len(tiktok_proposals) + len(tiktok_accepted_proposals) +  len(tiktok_active_proposals) + len(tiktok_pending_proposals) + len(tiktok_posting_proposals)

    
    context = {
        'account':brand,
        'ig_sent_proposals': ig_proposals,
        'ig_payment_due_proposals' : ig_accepted_proposals,
        'ig_active_proposals' : ig_active_proposals,
        'ig_content_approval_proposals' : ig_pending_proposals,
        'ig_posting_proposals' : ig_posting_proposals,

        'ig_num': ig_num , 
        'tiktok_num': tiktok_num,

        'tiktok_sent_proposals': tiktok_proposals,
        'tiktok_payment_due_proposals' : tiktok_accepted_proposals,
        'tiktok_active_proposals' : tiktok_active_proposals,
        'tiktok_content_approval_proposals' : tiktok_pending_proposals,
        'tiktok_posting_proposals' : tiktok_posting_proposals
    }

    links = {}
    num = len(ig_pending_proposals) + len(tiktok_pending_proposals)
    #if there are pending proposals , display the link in navbar
    if ig_pending_proposals.exists() or tiktok_pending_proposals.exists():
        links["content_approval"]= {
                    'url' : reverse_lazy("pending_content_approval"),
                'name' : f'Content Approval ({num})'
            }


    context['links'] = links
    return render(request, 'base/brand_proposals.html', context)

class CreateBrandProposal(UserPassesTestMixin ,LoginRequiredMixin , FormView):
    form_class = BrandProposalForm
    template_name = "base/create_proposal.html"

    def get_success_url(self):
        brand = get_object_or_404(BrandProfile , user=self.request.user)
        return reverse("brand_proposals" , kwargs={"brand_id": brand.id})

    def test_func(self):
        try:
            brand = get_object_or_404(BrandProfile , user = self.request.user)
        except Http404:
            return False
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        context['username'] = brand.brand_name
        return context
        


    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        creator = get_object_or_404(CreatorProfile , id = self.kwargs.get('creator_id'))
        ig_account = get_object_or_404(InstagramAccountDashBoard , creator = creator)
        try:
            active_proposal = BrandDeal.objects.get(brand=brand , platform = BrandDeal.Platforms.INSTAGRAM , creator=creator , ig_account = ig_account)
        except BrandDeal.DoesNotExist :
            proposal= BrandDeal.objects.create(
                brand = brand,
                creator = creator,
                ig_account = ig_account,

                platform = BrandDeal.Platforms.INSTAGRAM ,

                description = form.cleaned_data['description'],
                timeline = (form.cleaned_data['timeline']+3),
                proposed_amount = form.cleaned_data['proposed_amount'],
                product_link = form.cleaned_data['product_link'],
                content_type = form.cleaned_data['content_type'],
                proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT
            )
            # Send email to the creator about the new proposal (Template tag set to new simpler)
            template_id = 19
            to = [{"email": creator.contact_email}]
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                template_id=template_id,
                params={
                    'creator_name': proposal.creator.name,  # Add any parameters you want to include in the email
                    'link': self.request.build_absolute_uri(reverse("accept_or_reject" , kwargs={"proposal_id" : proposal.id }))
                }
            )

            transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            try:
                api_response = transac_api_instance.send_transac_email(send_smtp_email)
                print("API Response:", api_response)
            #if email is not sent , then redirects to home with a message saying send proposal again
            except ApiException as e:
                print(f"Error: {e}")
                proposal.delete()
                messages.add_message(self.request, messages.ERROR, "Failed to send email notification. Please Send the Proposal Again")
                return redirect(reverse_lazy("home"))
            except Exception as e:
                print(f"Error: {e}")
                proposal.delete()
                messages.add_message(self.request, messages.ERROR, "An unexpected error occurred while sending email. Please Send the Proposal Again")
                return redirect(reverse_lazy("home"))
            
            return super().form_valid(form)

        else:
            messages.add_message(self.request,messages.ERROR , "You already have a Active Brand Deal with the Creator")
            return redirect(reverse_lazy("home"))

# EVERYTHING SAME WITH CREATEBRANDPROPOSAL EXCEPT IT AUTOMATICALLY SETS CONTENT TYPE AS TIKTOK HAS ONLY TIKTOK SHORT CONTENT TYPE.
class CreateTiktokBrandProposal(UserPassesTestMixin ,LoginRequiredMixin , FormView):
    form_class = TiktokBrandProposalForm
    template_name = "base/create_proposal.html"
    
    def get_success_url(self):
        brand = get_object_or_404(BrandProfile , user=self.request.user)
        return reverse("brand_proposals" , kwargs={"brand_id": brand.id})

    def test_func(self):
        try:
            brand = get_object_or_404(BrandProfile , user = self.request.user)
        except Http404:
            return False
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        context['username'] = brand.brand_name
        return context


    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        creator = get_object_or_404(CreatorProfile , id = self.kwargs.get('creator_id'))
        tiktok_account = get_object_or_404(TiktokDashboard , creator = creator)
        try:
            active_proposal = BrandDeal.objects.get(brand=brand , platform = BrandDeal.Platforms.TIKTOK , creator=creator , tiktok_account = tiktok_account)
        except BrandDeal.DoesNotExist :
            proposal= BrandDeal.objects.create(
                brand = brand,
                creator = creator,
                tiktok_account = tiktok_account,

                platform = BrandDeal.Platforms.TIKTOK,

                description = form.cleaned_data['description'],
                timeline = (form.cleaned_data['timeline']+3),
                proposed_amount = form.cleaned_data['proposed_amount'],
                product_link = form.cleaned_data['product_link'],
                content_type = BrandDeal.Content_Choices.TIKTOK_SHORT,
                proposal_status = BrandDeal.Proposal_Status.PROPOSAL_SENT
            )
            # Send email to the creator about the new proposal (Template tag set to new simpler)
            template_id = 19
            to = [{"email": creator.contact_email}]
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                template_id=template_id,
                params={
                    'creator_name': proposal.creator.name,  # Add any parameters you want to include in the email
                    'link': self.request.build_absolute_uri(reverse("accept_or_reject" , kwargs={"proposal_id" : proposal.id }))
                }
            )

            transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            try:
                api_response = transac_api_instance.send_transac_email(send_smtp_email)
                print("API Response:", api_response)
            #if email is not sent , then redirects to home with a message saying send proposal again
            except ApiException as e:
                print(f"Error: {e}")
                proposal.delete()
                messages.add_message(self.request, messages.ERROR, "Failed to send email notification. Please Send the Proposal Again")
                return redirect(reverse_lazy("home"))
            except Exception as e:
                print(f"Error: {e}")
                proposal.delete()
                messages.add_message(self.request, messages.ERROR, "An unexpected error occurred while sending email. Please Send the Proposal Again")
                return redirect(reverse_lazy("home"))
            
            return super().form_valid(form)

        else:
            messages.add_message(self.request,messages.ERROR , "You already have a Active Brand Deal with the Creator")
            return redirect(reverse_lazy("home"))
        
            
@login_required 
def accept_or_reject(request , proposal_id):
    proposal = get_object_or_404(BrandDeal , id = proposal_id)
    #restrict other users from using link
    if proposal.creator.user != request.user :
            raise PermissionDenied
    links={}
    active_proposals = BrandDeal.objects.filter(creator=proposal.creator , proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE)
    if active_proposals.exists() :
        links['active_proposals'] = {
                'url': reverse("creator_active_proposals" , kwargs={"creator_id":proposal.creator.id}),
                'name': "Active Proposals"
        }
    ig_dashboard = InstagramAccountDashBoard.objects.filter(creator = proposal.creator)
    tiktok_dashboard = TiktokDashboard.objects.filter(creator = proposal.creator)
    if ig_dashboard.exists() or tiktok_dashboard.exists():
        links['manage_integrations'] = {
                'url': reverse("integration_dashboard" , kwargs={"pk":proposal.creator.id}),
                'name': "Manage Integrations"
                }
    links['payment_dashboard'] = {
            'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":proposal.creator.id}),
            'name': "Payment Dashboard"
            }

    context = {
        'proposal' : proposal,
        "links" : links
    }


    return render(request , 'base/creator_accept_or_reject.html' , context)

        

@login_required
def accept_brand_proposal(request , proposal_id , slug=None):
    proposal = get_object_or_404(BrandDeal , id = proposal_id)
    if request.user != proposal.creator.user:
        raise PermissionDenied
    proposal.proposal_status = BrandDeal.Proposal_Status.PROPOSAL_ACCEPTED
    proposal.save()
    # Send email to the brand with a link to the payment page
    brand_email = proposal.brand.email
    payment_link = request.build_absolute_uri(
        reverse("brand_proposal_payment", kwargs={"proposal_id": proposal.id}))
    # Prepare the email details
    template_id = 20 #new template id set
    to = [{"email": brand_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        template_id=template_id,
        params={
            'brand_name': proposal.brand.brand_name,
            'link': payment_link,
        }
    )
    transac_api_instance =sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    try:
        api_response = transac_api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully:", api_response)
        proposal.proposal_status = BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE
        proposal.save()
    except ApiException as e:
        print(f"Error: {e}")
        messages.add_message(request, messages.ERROR, "Failed to send email notification. Try Again or Contact Support")
        unsent_email = UnsentEmails.objects.create(
            purpose = "Informing Brand that Creator has Accepted their Brand Proposal",
            send_to_email = brand_email,
            send_to = proposal.brand,
            send_from = proposal.creator,
            param_link = payment_link
        )

    return redirect(reverse_lazy("home"))

#Implement brand emailing feature when creator rejects proposal
@login_required
def reject_brand_proposal(request , proposal_id , slug=None):
    proposal = get_object_or_404(BrandDeal , id = proposal_id)
    if request.user != proposal.creator.user:
        raise PermissionDenied
    proposal.proposal_status = BrandDeal.Proposal_Status.PROPOSAL_REJECTED
    proposal.save()


    return redirect(reverse_lazy("home"))

@login_required
def creator_active_proposals(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    if creator.user != request.user:
        raise PermissionDenied
    #active proposals is actually proposals that have been accepted and have been sent for payment , hence here DEAL_PAYMENT_DUE STATUS IS USED for Accepted Proposals
    ig_accepted_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.INSTAGRAM , proposal_status =BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE)
    ig_active_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.INSTAGRAM , proposal_status =BrandDeal.Proposal_Status.DEAL_ACTIVE)
    ig_approval_due_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.INSTAGRAM , proposal_status =BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    ig_posting_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.INSTAGRAM , proposal_status =BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT)
    ig_completed_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.INSTAGRAM , proposal_status =BrandDeal.Proposal_Status.DEAL_COMPLETED)
    

    tiktok_accepted_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.TIKTOK , proposal_status =BrandDeal.Proposal_Status.DEAL_PAYMENT_DUE)
    tiktok_active_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.TIKTOK , proposal_status =BrandDeal.Proposal_Status.DEAL_ACTIVE)
    tiktok_approval_due_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.TIKTOK , proposal_status =BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    tiktok_posting_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.TIKTOK , proposal_status =BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT)
    tiktok_completed_proposals = BrandDeal.objects.filter( creator = creator , platform= BrandDeal.Platforms.TIKTOK , proposal_status =BrandDeal.Proposal_Status.DEAL_COMPLETED)

    ig_num = len(ig_accepted_proposals) + len(ig_active_proposals) + len(ig_approval_due_proposals) + len(ig_posting_proposals) + len(ig_completed_proposals)
    tiktok_num = len(tiktok_accepted_proposals) + len(tiktok_active_proposals) + len(tiktok_approval_due_proposals) + len(tiktok_posting_proposals) + len(tiktok_completed_proposals)

    links={}
    ig_dashboard = InstagramAccountDashBoard.objects.filter(creator = creator)
    tiktok_dash = TiktokDashboard.objects.filter(creator=creator)
    if ig_dashboard.exists() or tiktok_dash.exists():
        links['manage_integrations'] = {
                'url': reverse("integration_dashboard" , kwargs={"pk":creator.id}),
                'name': "Manage Integrations"
                }
    links['payment_dashboard'] = {
            'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":creator.id}),
            'name': "Payment Dashboard"
            }
    context = {
        "account":creator,
        "links": links,

        'ig_accepted_proposals': ig_accepted_proposals,
        'ig_active_proposals': ig_active_proposals,
        'ig_approval_due_proposals': ig_approval_due_proposals,
        'ig_posting_proposals': ig_posting_proposals,
        'ig_completed_proposals': ig_completed_proposals,

        "ig_num": ig_num,
        "tiktok_num": tiktok_num,

        'tiktok_accepted_proposals': tiktok_accepted_proposals,
        'tiktok_active_proposals': tiktok_active_proposals,
        'tiktok_approval_due_proposals': tiktok_approval_due_proposals,
        'tiktok_posting_proposals': tiktok_posting_proposals,
        'tiktok_completed_proposals': tiktok_completed_proposals

        

    }
    

    return render(request , 'base/creator_active_proposals.html' , context)

@login_required
def creator_payment_dashboard(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    if creator.user != request.user :
        raise PermissionDenied
    paid_proposals = BrandDeal.objects.filter(
        Q(creator=creator) & (Q(proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE) | (Q(proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING) | (Q(proposal_status = BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT))))
    )
    pending_payment = decimal.Decimal(0)
    for proposal in paid_proposals:
        pending_payment += round(decimal.Decimal(0.95) * proposal.proposed_amount, 1)

    links={}
    if paid_proposals.exists():
        links['active_proposals'] = {
                'url': reverse("creator_active_proposals" , kwargs={"creator_id":creator.id}),
                'name': "Active Proposals"
        }
    #shows manage integrations link in navbar only if dashboard exists
    dashboard = InstagramAccountDashBoard.objects.filter(creator = creator)
    tiktok_dashboard = TiktokDashboard.objects.filter(creator=creator)
    if dashboard.exists() or tiktok_dashboard.exists():
        links['manage_integrations'] = {
                'url': reverse("integration_dashboard" , kwargs={"pk":creator.id}),
                'name': "Manage Integrations"
                }
    context = {
        'pending_payment' : pending_payment,
        'paid_proposals' : paid_proposals,
        'account':creator,
        "links":links
    }

    return render(request , 'base/creator_payment_dashboard.html' , context)

@login_required
def brand_proposal_payment(request , proposal_id):
    proposal = get_object_or_404(BrandDeal , id = proposal_id)

    if proposal.brand.user != request.user :
        raise PermissionDenied

    paypal_dict = {
        'business': 'wearaiofficial@gmail.com',
        'amount': f"{proposal.proposed_amount:.2f}",
        'currency_code':'USD',
        'item_name': "Brand Promotion Deal" ,
        'return': request.build_absolute_uri(reverse("successfull_payment" , kwargs={"proposal_id": proposal.id})), #change this
        'cancel_return':request.build_absolute_uri(reverse("payment_failed" , kwargs={"brand_id":proposal.brand.id})) #change this 
    }

    form = PayPalPaymentsForm(initial = paypal_dict)
    context = {
        'proposal':proposal,
        'form': form
    }

    return render(request , "base/brand_proposal_payment.html" ,context)

@login_required
def successfull_payment(request , proposal_id):
    proposal = get_object_or_404(BrandDeal , id= proposal_id)
    if proposal.brand.user != request.user :
        raise PermissionDenied
    proposal.proposal_status = BrandDeal.Proposal_Status.DEAL_PAID
    proposal.date_paid = timezone.now()
    proposal.save()
    proposed_date = proposal.date_paid + datetime.timedelta(days = proposal.timeline)
    proposal.duration_left = proposed_date - timezone.now()
    proposal.save()
    # Send email to the creator
    creator_email = proposal.creator.contact_email
    view_link = request.build_absolute_uri(
        reverse("creator_active_proposals", kwargs={"creator_id": proposal.creator.id}))

    # Received Payment (to Creator) - Set new template id ✅
    template_id = 21
    send_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": creator_email}],
        template_id=template_id,
        params={
            "creator_name": proposal.creator.name,
            #"amount": str(proposal.proposed_amount),
            #"payment_date": proposal.date_paid.strftime("%Y-%m-%d"),
            #"view_link": view_link
        }
    )

    # Initialize the API client
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Send the email
    try:
        api_response = api_instance.send_transac_email(send_email)
        print("Email sent successfully to the creator:", api_response)
    #correct error handling to be done
    except ApiException as e:
        print("Error sending email to the creator:", e)
        messages.add_message(request, messages.ERROR, f"Email Not Sent : {e}")
        #logs the email as unsent
        unsent_email = UnsentEmails.objects.create(
            purpose = "Brand Deal Payment Completed",
            send_to_email = "creator_email",
            send_to = proposal.creator,
            send_from = proposal.brand,
            param_link = view_link,
        )
        return redirect(reverse_lazy('home'))
    else:
        proposal.proposal_status = BrandDeal.Proposal_Status.DEAL_ACTIVE
        proposal.save()
        return render(request , 'base/successfull_payment.html')


@login_required
def payment_failed(request , brand_id):
    brand = get_object_or_404(BrandProfile , id=brand_id) 
    if brand.user != request.user :
        raise PermissionDenied

    context = {
        'brand_id':brand_id
    }
    
    return render(request , 'base/payment_failed.html', context)
    
@login_required
def content_approval_process(request, proposal_id ):
    transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    creator = get_object_or_404(CreatorProfile, user=request.user)
    proposal = get_object_or_404(BrandDeal, id=proposal_id)
    
    content_approval , created  = Content_Approval_Media.objects.get_or_create(proposal = proposal)
    
    if proposal.creator != creator:
        raise PermissionDenied
    if request.method == 'POST':
        image= request.FILES.get("image")
        video= request.FILES.get('video') 
        if image is not None:
            content_approval.image = image
        if video is not None:
            content_approval.video = video
        content_approval.save()

        # Sending using Brevo Email API
        template_id = 22
        # Ensure this is uncommented if needed
        approve_url = request.build_absolute_uri(reverse("brand_content_review", kwargs={"proposal_id": proposal.id}))
        brand_email = proposal.brand.email  # Get the brand's email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": brand_email}],
            template_id=template_id,
            params={
                "brand_name": proposal.brand.brand_name,
                "link": approve_url,
            }
        )
        # Send the email
        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
            proposal.proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING
            proposal.save()
        except ApiException as e:
            print(f"Error: {e}")
            messages.add_message(request, messages.ERROR, f"Content Approval Email Error: {e}")
            #loggging the unsent email
            unsent_email = UnsentEmails.objects.create(
                purpose = "Informing Brand that Content has been submitted for Approval by Creator",
                send_to_email = brand_email,
                send_from = proposal.creator ,
                send_to = proposal.brand ,
                param_link = approve_url
            )
        return redirect(reverse("creator_active_proposals", kwargs={"creator_id": creator.id}))
    else:
        return render(request, 'base/content_approval_form.html')

@login_required
def brand_pending_approval_view(request):
    brand_profile = get_object_or_404(BrandProfile , user = request.user)
    ig_proposals = BrandDeal.objects.filter(brand = brand_profile , platform = BrandDeal.Platforms.INSTAGRAM ,proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
    tiktok_proposals = BrandDeal.objects.filter(brand = brand_profile , platform = BrandDeal.Platforms.TIKTOK ,proposal_status = BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)

    context = {
        "ig_pending_proposals": ig_proposals,
        "tiktok_pending_proposals": tiktok_proposals,
        "account": brand_profile,
    }

    links = {}
    links['your_proposals'] = {
        'url': reverse("brand_proposals" , kwargs={"brand_id":brand_profile.id}),
        'name': "Your Proposals"
    }
    context['links'] = links

    return render(request , 'base/brand_content_approval.html' , context)

@login_required
def brand_content_review(request , proposal_id):
    approval_content = get_object_or_404(Content_Approval_Media , proposal__id = proposal_id)
    proposal = get_object_or_404(BrandDeal , id = proposal_id)
    if proposal.brand.user != request.user :
        raise PermissionDenied 

    if request.method == "POST":
        remarks = request.POST.get('remarks')
        auto_complete = request.POST.get('auto-complete') #returns none if checkbox is unchecked
        if remarks :
            approval_content.remarks = remarks
        if auto_complete is None :
            approval_content.autocomplete = False
        approval_content.save()
        return redirect(reverse('approve_content' , kwargs={"proposal_id": proposal.id}))

    else:
        links = {}
        pending_proposals = BrandDeal.objects.filter(brand = proposal.brand , proposal_status=BrandDeal.Proposal_Status.DEAL_CONTENT_APPROVAL_PENDING)
        your_proposals = BrandDeal.objects.filter(brand=proposal.brand) 
        if pending_proposals.exists():
            links['content_approval'] = {
                "url": reverse_lazy("pending_content_approval"),
                "name": f"Content Approval ({len(pending_proposals)})"
            }
        if your_proposals.exists():
            links['your_proposals'] ={
                'url': reverse("brand_proposals" , kwargs={"brand_id": proposal.brand.id}),
                'name': "Your Proposals"
            }

        context = {
            "content": approval_content,
            "content_list": approval_content,
            "links": links
        }

        return render(request , 'base/brand_content_review.html' , context) 

@login_required
def approve_content(request , proposal_id):
    approved_content = get_object_or_404(Content_Approval_Media , proposal__id = proposal_id)

    proposal = get_object_or_404(BrandDeal , id=proposal_id)
    
    transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    template_id = 23 #new template id is set

    if approved_content.remarks :
        remarks = approved_content.remarks
    else:
        remarks = "No Remarks"

    to = [{"email": proposal.creator.contact_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        template_id=template_id,
        params={
            "creator_name": proposal.creator.name,
            "remarks" : remarks,
            "approved_date": timezone.now().strftime("%Y-%m-%d"),
        }
    )

    try:
        api_response = transac_api_instance.send_transac_email(send_smtp_email)
        print("API Response:", api_response)
    except ApiException as e:
        print(f"Error: {e}")
        messages.add_message(request, messages.ERROR, f"Content Approval Email Error: {e}")
        return redirect(reverse("brand_content_review" , kwargs={"proposal_id": proposal.id}))
    else:
        proposal.proposal_status = BrandDeal.Proposal_Status.DEAL_POSTING_CONTENT
        proposal.auto_complete = approved_content.autocomplete
        proposal.save()

        return render(request, 'base/approved.html')

@login_required
def claim_referral_bonus(request):
    profile = get_object_or_404(CreatorProfile, user=request.user)

    total_referrals = profile.referrals.count()  # Adjust based on your logic

    referral_bonus = 5 * total_referrals

    profile.balance += referral_bonus
    profile.save()

    # Send response back (for example, in a JSON response)
    return JsonResponse({'success': True, 'new_balance': profile.balance})



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    form_class= PasswordResetForm
    template_name = 'base/password_reset.html'
    email_template_name = 'base/password_reset_email.html'
    subject_template_name = 'base/password_reset_subject.txt'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
       response = super().form_valid(form)
       try:
        user = EmailUser.objects.get(email=form.cleaned_data['email'])
       except EmailUser.DoesNotExist:
        # Optionally handle the case where the email doesn't exist
        messages.add_message(self.request, messages.INFO ,"No account found with this email address.")
        return response
       
       token = default_token_generator.make_token(user)
       uid = urlsafe_base64_encode(force_bytes(user.pk))

       self.send_mail(
           to_email=form.cleaned_data['email'],
           context={'uid': uid, 'token': token},
       )
       messages.add_message(self.request, messages.INFO, "We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly. If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder.")
       return response

    #bypassing django's smtp email sending with BREVO API TRANSACTION EMAIL 
    def send_mail(self , context , to_email):
        transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        template_id = 13
        to = [{"email": to_email}]
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
             params={
                'link': self.request.build_absolute_uri(reverse_lazy("password_reset_confirm", kwargs={"uidb64": context["uid"], "token": context["token"]}))
            }
        )
        
        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
            print("Email sent successfully.")
            return True
        except ApiException as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        

@login_required
def tiktok_authorize(request):
    authorization_code = request.GET.get('code')
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    if not authorization_code:
        authorization_data = {
            'client_key' : TIKTOK_CLIENT_KEY,
            'response_type': "code",
            'redirect_uri': request.build_absolute_uri(reverse_lazy("tiktok_authorize")),
            'scope': "user.info.basic,user.info.profile,user.info.stats",
            "state": "some random_state",
            'code_challenge': code_challenge,
            'code_challenge_method': "S256"
        }
        print(authorization_data['redirect_uri'])
        #encoding authorization parameters into the url
        authorization_url = f"https://www.tiktok.com/v2/auth/authorize?{urllib.parse.urlencode(authorization_data)}"
        print(authorization_url)
        return redirect(authorization_url)
    access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        'client_key': TIKTOK_CLIENT_KEY,
        'client_secret': TIKTOK_CLIENT_SECRET,
        'code': authorization_code,
        'redirect_uri': request.build_absolute_uri(reverse_lazy("tiktok_authorize")),
        'grant_type': 'authorization_code',
        
    }
    response = requests.post(access_token_url , data=payload)
    print(response.json())
    if response.status_code != 200:
        return HttpResponse(f"ERROR: {response.status_code}")
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    error = response.json().get("error")
    if not access_token or not refresh_token:
        if error:
            return HttpResponse(f"{error} , Please try again")
    creator_profile = get_object_or_404(CreatorProfile , user = request.user)
    tiktok_dash,created = TiktokDashboard.objects.get_or_create(
            creator = creator_profile,
            access_token = hash_token(access_token),
            refresh_token = hash_token(refresh_token)
    )    
    return redirect(reverse("tiktok_get_data" , kwargs={"dash_id": tiktok_dash.id}))
    

@login_required
def tiktok_user_data(request , dash_id):
    tiktok_dash = get_object_or_404(TiktokDashboard , id=dash_id)
    if tiktok_dash.creator.user != request.user:
        raise PermissionDenied
    access_token = unhash_token(tiktok_dash.access_token)
    refresh_token = unhash_token(tiktok_dash.refresh_token)
    user_data_url = "https://open.tiktokapis.com/v2/user/info/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'fields': 'avatar_url,open_id,union_id,display_name,bio_description,profile_deep_link,is_verified,username,follower_count,likes_count,video_count'  # Requesting specific fields
    }
    user_data = requests.get(user_data_url , headers=headers , params=params)
    try:
        user_data_json = user_data.json()
    except ValueError:
        return JsonResponse({"error": "Invalid JSON response", "details": user_data.text}, status=400)
    if user_data.status_code != 200:
        user_info_error = user_data_json.get('error').get('code')
        if user_info_error == "access_token_invalid":
                if refresh_token:
                    payload = {
                    'client_key': TIKTOK_CLIENT_KEY,
                    'client_secret': TIKTOK_CLIENT_SECRET,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                    }
                    access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"
                    try:
                        response = requests.post(access_token_url , data=payload)
                        if response.status_code == 200:
                            print("Access Token Fetch Successfull")
                            refreshed_access_token = response.json().get("access_token")
                            refreshed_refresh_token = response.json().get("refresh_token")
                            if refreshed_access_token is None or refreshed_refresh_token is None:
                                return HttpResponse("API Critical Error : Access Token Not Found !!")
                            else:
                                tiktok_dash.access_token = hash_token(refreshed_access_token)
                                tiktok_dash.refresh_token =  hash_token(refreshed_refresh_token)
                                tiktok_dash.save()
                                return redirect(reverse("tiktok_get_data" , kwargs={"dash_id": tiktok_dash.id}))
                    except ValueError:
                        return JsonResponse(response.json() , status= response.status_code)
            
        else:
            print(user_data_json)
            return JsonResponse({"error": user_data_json, "details": user_data.text}, status=400)

    user_info = user_data_json.get('data', {}).get('user', {})
    if not user_info:
        return JsonResponse({"error": "User info not found in response"}, status=400)

    # Example of the user data you might want to return
    user_info_response = {
        'avatar_url': user_info.get('avatar_url'),
        'open_id': user_info.get('open_id'),
        'union_id': user_info.get('union_id'),#not used rn
        'display_name': user_info.get('display_name'),
        'profile_deep_link': user_info.get('profile_deep_link'),
        'is_verified': user_info.get('is_verified'),
        'follower_count': user_info.get('follower_count'),
        'username': user_info.get('username'),
        'likes_count': user_info.get('likes_count'),
        'video_count': user_info.get('video_count'),
    }

    tiktok_dash.avatar_url = user_info_response['avatar_url']
    tiktok_dash.open_id = user_info_response['open_id']
    tiktok_dash.display_name = user_info_response["display_name"]
    tiktok_dash.profile_deep_link = user_info_response['profile_deep_link']
    tiktok_dash.is_verified = user_info_response['is_verified']
    tiktok_dash.follower_count = user_info_response['follower_count']
    tiktok_dash.likes_count = user_info_response['likes_count']
    tiktok_dash.video_count = user_info_response['video_count']
    tiktok_dash.save()
    if tiktok_dash.follower_count > 0  and tiktok_dash.video_count > 0:
        tiktok_dash.engagement_rate = decimal.Decimal((tiktok_dash.likes_count/(tiktok_dash.likes_count + (tiktok_dash.video_count * tiktok_dash.follower_count)))*100)
    else:
        tiktok_dash.engagement_rate = decimal.Decimal(0)    
    tiktok_dash.save()
    
    # Return the user data in a JsonResponse or render a template as needed
    return redirect(reverse("edit_tiktok_dashboard" , kwargs={"pk": tiktok_dash.id}))
    # Return user data or render a template

class TiktokDashboardEdit(UpdateView , LoginRequiredMixin , UserPassesTestMixin):
    model = TiktokDashboard
    fields = ['pricing_per_promotion' , 'tags']
    template_name = 'base/tiktok_dashboard_edit.html'

    
    def test_func(self):
        tiktok_dash = get_object_or_404(TiktokDashboard , id=self.kwargs.get('pk') )
        if tiktok_dash.creator.user == self.request.user :
            return True
        return False
    
    def get_success_url(self):
        creator = get_object_or_404(CreatorProfile , user = self.request.user)
        return reverse("integration_dashboard" , kwargs={"pk":creator.id})

@login_required
def referral_dashboard(request , creator_id):
    creator_profile = get_object_or_404(CreatorProfile , id=creator_id)
    if creator_profile.user != request.user :
        raise PermissionDenied
    context = {
        'creator' : creator_profile
    }
    if creator_profile.referral_link_code:
        referral_link = request.build_absolute_uri(reverse_lazy('signup'))
        context["referral_link"] = f"{referral_link}{creator_profile.referral_link_code}" 
    links ={}
    
    links['payment_dashboard'] = {
            'url': reverse("creator_payment_dashboard" , kwargs={"creator_id":creator_profile.id}),
            'name': "Payment Dashboard"
    }

    links['update_profile'] = {
            'url': reverse("creator_profile_update" , kwargs={"pk":creator_profile.id}),
            'name': "Update Profile"
    }


    context['links'] = links
    context['username']= creator_profile.name
    return render(request , "base/referral_dashboard.html" , context=context)

@login_required
def create_referral_link(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id=creator_id)
    if creator.user != request.user :
        raise PermissionDenied
    if not creator.referral_link_code :
        creator.generate_referral_link_code()
    return redirect(reverse("referral_dashboard" , kwargs={"creator_id" : creator.id}))
    




#ADMIN COMMANDS (DB Update)
def db_eng_rate_update(request , perm_code):
    if perm_code == "0212":
        ig_accounts = InstagramAccountDashBoard.objects.all()
        if ig_accounts:
            for account in ig_accounts: 
                print(f"{account.engagement_rate}- Earlier EG RAte" )
                engagement_rate = round(decimal.Decimal((account.engagement / (account.engagement + account.followers))*100),2)
                account.engagement_rate = engagement_rate
                account.average_rate = round((account.engagement_rate/ decimal.Decimal(100)) * decimal.Decimal(0.02) * (decimal.Decimal(account.followers) ** decimal.Decimal(1)))
                if account.average_rate < 5 :
                    account.average_rate = 5
                account.save()
                print(f"{account.engagement_rate}- Normalized EG RAte" )  
                print(f"{account.average_rate}- Normalized Avg Rate" )  
                print("------------------")
            return HttpResponse("DB Engagement Values Updated Successfully")
        else:
            print("No ig accounts found")
    else:
        raise PermissionDenied