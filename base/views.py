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


from users.forms import EmailUserCreationForm
from .forms import AccountTypeForm , AccountIntegrationForm , BrandProposalForm ,TiktokBrandProposalForm, DashboardImageForm , EmailVerificationForm , BrandSubscriptionForm
from users.models import EmailUser
from .models import CreatorProfile ,BrandProfile , BrandProposal , InstagramAccountDashBoard , Content_Approval_Images , VerifyEmail,Referral , TiktokDashboard , TiktokProposal



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



# Create your views here.

def landing_page(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("home"))
    else:
        return render(request ,'base/landing_brand.html')

def landing_page_creator(request):
    return render(request , 'base/landing_creator.html')

def landing_page_pricing(request):
    return render(request , 'base/landing_pricing.html')


@login_required
def home(request, slug=None):

    creator_account = CreatorProfile.objects.filter(user = request.user)
    brand_account = BrandProfile.objects.filter(user = request.user)
    context = {}
    if creator_account.exists():
        ig_proposals = BrandProposal.objects.filter(creator = creator_account[0] , proposal_status = BrandProposal.Proposal_Status.REQUESTED)
        tiktok_proposals = TiktokProposal.objects.filter(creator = creator_account[0] , proposal_status = TiktokProposal.Proposal_Status.PROPOSAL_SENT)
        ig_account = InstagramAccountDashBoard.objects.filter(creator = creator_account[0])
        tiktok_account = TiktokDashboard.objects.filter(creator = creator_account[0])
        #change the ig_active_proposals status-es
        ig_active_proposals = BrandProposal.objects.filter(creator = creator_account[0] , proposal_status = BrandProposal.Proposal_Status.PAID)
        tiktok_active_proposals = TiktokProposal.objects.filter(creator = creator_account[0] , proposal_status = TiktokProposal.Proposal_Status.DEAL_ACTIVE)
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
                    creator_accounts = TiktokDashboard.objects.filter(tags__icontains = search_query).order_by('followers')
                else:
                    creator_accounts = TiktokDashboard.objects.filter(tags__icontains = search_query).order_by('-followers')
            
            context['social_media'] = social_media
            context['creators'] = creator_accounts
    
        #The same brand code for both tiktok and ig media because brand proposals and brand account is both same 
        context['account'] = brand_account[0]
        account = brand_account[0]
        if account.brand_name:
            context['username'] = account.brand_name
        context['pending_proposals'] = BrandProposal.objects.filter(brand = account ,proposal_status = BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING)
        your_proposals = BrandProposal.objects.filter(brand=account)
        links = {}
        
        #content approval pending link to be added to dynamic navbar links
        if context['pending_proposals'].exists():
            num = len(context['pending_proposals'])
            links["content_approval"]= {
                'url' : reverse_lazy("pending_content_approval"),
                'name' : f'Content Approval ({num})'
            }
        #your proposal link added to DN(Dynamic navbar) Links
        if your_proposals.exists():
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

    def get_success_url(self):
        return reverse_lazy("account_selection")
    
    def form_valid(self , form):
        user = form.save()
        if user is not None:

            """"
=======
            '''
>>>>>>> d6db619a5c70cdc9af0a12524861e1b5aedbdb1f
            referral_code = Referral.generate_code()
            Referral.objects.create(user=user, code=referral_code)

            # Handle the referral logic
            ref_code = self.request.GET.get('ref', None)
            if ref_code:
                try:
                    referrer = Referral.objects.get(code=ref_code).user
                    referrer_profile = referrer.creatorprofile if hasattr(referrer,
                                                                          'creatorprofile') else referrer.brandprofile
                    referrer_profile.referrals += 1
                    referrer_profile.save()

                    # Optional: Give reward for referral
                    messages.success(self.request,
                                     f"Referral successful! Thank you for joining via {referrer.username}'s referral.")
                except Referral.DoesNotExist:
<<<<<<< HEAD
                    messages.error(self.request, "Invalid referral code.")"""


    

            login(self.request , user)
        return super(EmailSignUp,self).form_valid(form)    
    
    def test_func(self):
        return self.request.user.is_anonymous
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy("home"))
    

class AccountType(UserPassesTestMixin ,FormView,LoginRequiredMixin):
    form_class = AccountTypeForm
    template_name = "base/account_selection.html"
    
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
        self.brand_account = False
        account_type = form.cleaned_data['account_type']
        if account_type == "brand":
            self.brand_account = True
            account,created = BrandProfile.objects.get_or_create(user = self.request.user , email = self.request.user.email)
        else:
            account,created = CreatorProfile.objects.get_or_create(user = self.request.user, contact_email =self.request.user.email)
        account.save()
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
            email = creator_profile.contact_email,
            account_type = VerifyEmail.AccountType.CREATOR,
        )
        if created == False and verification.verified == True:
            form.save(commit=True)
            self.verify_id = None
        else:
            creator_profile.contact_email = None
            verification.generate_verification_code()
            self.verify_id = verification.id
            
            #sending Verification email using send_verification_email() method defined in the VerifyEmail Model's methods
            if verification.verification_code:
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
            account_type = VerifyEmail.AccountType.BRAND,
        )

        if created == False and verification.verified == True:
            form.save(commit=True)
            self.verify_id = None
        else:
            brand_profile.email = None
            brand_profile.save()
            verification.generate_verification_code()
            self.verify_id = verification.id

            #same method as in CreatorProfileUpdate
            if verification.verification_code:
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
        if (verification.email != self.request.user.email):
            return False  # Return False if creator not found
        return True


    def form_valid(self, form):
        email_list_id = []
        email_code = form.cleaned_data['email_code']
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
        ig_active_proposals = BrandProposal.objects.filter(creator = creator_profile , proposal_status = BrandProposal.Proposal_Status.PAID)
        tiktok_active_proposals = TiktokProposal.objects.filter(creator = creator_profile , proposal_status = TiktokProposal.Proposal_Status.DEAL_ACTIVE)
        if ig_active_proposals.exists() or tiktok_active_proposals.exists():
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
        avg_rate = (form.cleaned_data['story_rates'] + form.cleaned_data['reel_rates']) // 2
        engagement_rate = decimal.Decimal((form.cleaned_data['engagement'] / form.cleaned_data['followers'])*100)
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
        dashboard.average_rate = ((dashboard.story_rates + dashboard.reel_rates) // 2)
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
    
def brand_proposal_view(request , pk):
    proposal = get_object_or_404(BrandProposal , id=pk)
    if proposal.brand.user != request.user:
        raise PermissionDenied
    links = {}
    pending_proposals = BrandProposal.objects.filter(brand = proposal.brand , proposal_status = BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING)
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

def creator_proposal_view(request , pk , slug=None):
    if slug == None:
        proposal = get_object_or_404(BrandProposal , id = pk)
        social_media = "instagram"

    elif slug == "tiktok":
        proposal = get_object_or_404(TiktokProposal , id=pk )
        social_media = "tiktok"


    if proposal.creator.user != request.user :
            raise PermissionDenied
    links={}
    ig_active_proposals = BrandProposal.objects.filter(creator=proposal.creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    tiktok_active_proposals = TiktokProposal.objects.filter(creator=proposal.creator , proposal_status = TiktokProposal.Proposal_Status.DEAL_ACTIVE)
    if ig_active_proposals.exists() or tiktok_active_proposals.exists():
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
        'social_media': social_media,
        'proposal' : proposal,
        "links" : links
    }


    return render(request , 'base/creator_proposal_view.html' , context)





def get_brand_proposals(request, brand_id):
    brand = get_object_or_404(BrandProfile , id = brand_id)
    if brand.user != request.user:
        raise PermissionDenied
    proposals = BrandProposal.objects.filter(brand = brand , proposal_status = BrandProposal.Proposal_Status.REQUESTED)
    accepted_proposals = BrandProposal.objects.filter(brand =  brand , proposal_status = BrandProposal.Proposal_Status.ACCEPTED)
    paid_proposals = BrandProposal.objects.filter(brand =  brand , proposal_status = BrandProposal.Proposal_Status.PAID)
    pending_proposals = BrandProposal.objects.filter(brand= brand , proposal_status= BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING)
    context = {
        'account':brand,
        'proposals': proposals,
        'accepted_proposals' : accepted_proposals,
        'paid_proposals' : paid_proposals
    }

    links = {}
    num = len(pending_proposals)
    #if there are pending proposals , display the link in navbar
    if pending_proposals.exists():
        links["content_approval"]= {
                    'url' : reverse_lazy("pending_content_approval"),
                'name' : f'Content Approval ({num})'
            }


    context['links'] = links
    return render(request, 'base/brand_proposals.html', context)

class CreateBrandProposal(UserPassesTestMixin ,LoginRequiredMixin , FormView):
    form_class = BrandProposalForm
    template_name = "base/create_proposal.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        try:
            brand = get_object_or_404(BrandProfile , user = self.request.user)
        except Http404:
            return False
        else:
            return True



    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        creator = get_object_or_404(CreatorProfile , id = self.kwargs.get('creator_id'))
        ig_account = get_object_or_404(InstagramAccountDashBoard , creator = creator)
        try:
            active_proposal = BrandProposal.objects.get(brand=brand , creator=creator , account = ig_account)
        except BrandProposal.DoesNotExist :
            proposal= BrandProposal.objects.create(
            brand = brand,
            creator = creator,
            account = ig_account,
            
            description = form.cleaned_data['description'],
            timeline = (form.cleaned_data['timeline']+3),
            proposed_amount = form.cleaned_data['proposed_amount'],
            product_link = form.cleaned_data['product_link'],
            content_type = form.cleaned_data['content_type'],
            proposal_status = BrandProposal.Proposal_Status.REQUESTED

            )

            return super().form_valid(form)

        else:
            messages.add_message(self.request,messages.ERROR , "You already have a Active Brand Deal with the Creator")
            return redirect(reverse_lazy("home"))
        
class CreateTiktokBrandProposal(UserPassesTestMixin ,LoginRequiredMixin , FormView):
    form_class = TiktokBrandProposalForm
    template_name = "base/create_proposal.html"
    
    def get_success_url(self):
        return reverse_lazy("home_with_slug" , kwargs={"slug": "tiktok"})

    def test_func(self):
        try:
            brand = get_object_or_404(BrandProfile , user = self.request.user)
        except Http404:
            return False
        else:
            return True



    def form_valid(self, form):
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        creator = get_object_or_404(CreatorProfile , id = self.kwargs.get('creator_id'))
        tiktok_account = get_object_or_404(TiktokDashboard , creator = creator)
        try:
            active_proposal = TiktokProposal.objects.get(brand=brand , creator=creator , account = tiktok_account)
        except TiktokProposal.DoesNotExist :
            proposal= TiktokProposal.objects.create(
            brand = brand,
            creator = creator,
            account = tiktok_account,
            
            description = form.cleaned_data['description'],
            timeline = (form.cleaned_data['timeline']+3),
            proposed_amount = form.cleaned_data['proposed_amount'],
            product_link = form.cleaned_data['product_link'],
            proposal_status = TiktokProposal.Proposal_Status.PROPOSAL_SENT

            )
            #email sending feature (yet to be implemented)
            '''
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
        )

        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
        except ApiException as e:
            print(f"Error: {e}")
            messages.add_message(request, messages.ERROR, f"Content Approval Email Error: {e}")
        else:
            proposal.proposal_status = BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING
            proposal.save()           
        return redirect(reverse("creator_active_proposals", kwargs={"creator_id": creator.id}))

    else:
        return render(request, 'base/content_approval_form.html')

            '''


            return super().form_valid(form)

        else:
            messages.add_message(self.request,messages.ERROR , "You already have a Active Brand Deal with the Creator")
            return redirect(reverse_lazy("home"))
        
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = get_object_or_404(BrandProfile ,user = self.request.user)
        context['username'] = brand.brand_name
        return context
        


def accept_brand_proposal(request , proposal_id , slug=None):
    if slug is None:
        proposal = get_object_or_404(BrandProposal , id = proposal_id)
        if request.user != proposal.creator.user:
            raise PermissionDenied
        proposal.proposal_status = BrandProposal.Proposal_Status.ACCEPTED
        proposal.save()
        
    elif slug == "tiktok":
        proposal = get_object_or_404(TiktokProposal , id=proposal_id)
        if request.user != proposal.creator.user:
            raise PermissionDenied
        proposal.proposal_status = TiktokProposal.Proposal_Status.DEAL_PAYMENT_DUE
        proposal.save()

    return redirect(reverse_lazy("home"))

def reject_brand_proposal(request , proposal_id , slug=None):
    if slug is None:
        proposal = get_object_or_404(BrandProposal , id = proposal_id)
        if request.user != proposal.creator.user:
            raise PermissionDenied
        proposal.proposal_status = BrandProposal.Proposal_Status.REJECTED
        proposal.save()

    elif slug == "tiktok":
        proposal = get_object_or_404(TiktokProposal , id=proposal_id)
        if request.user != proposal.creator.user:
            raise PermissionDenied
        proposal.proposal_status = TiktokProposal.Proposal_Status.PROPOSAL_REJECTED
        proposal.save()

    return redirect(reverse_lazy("home"))

def creator_active_proposals(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    if creator.user != request.user:
        raise PermissionDenied
    ig_active_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    tiktok_active_proposals = TiktokProposal.objects.filter(creator=creator , proposal_status = TiktokProposal.Proposal_Status.DEAL_ACTIVE)
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
        "links": links
    }
    #sets proposal list to context variable only if it is not empty , else default None value is used
    context['ig_active_proposals'] = None
    context['tiktok_active_proposals'] = None

    if ig_active_proposals.exists():
        context['ig_active_proposals'] = ig_active_proposals
    if tiktok_active_proposals.exists():
        context['tiktok_active_proposals'] = tiktok_active_proposals
    
    
    return render(request , 'base/creator_active_proposals.html' , context)

def creator_payment_dashboard(request , creator_id):
    creator = get_object_or_404(CreatorProfile , id = creator_id)
    if creator.user != request.user :
        raise PermissionDenied
    paid_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    completed_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.COMPLETED)
    pending_payment = decimal.Decimal("0.00")
    for proposal in paid_proposals:
        pending_payment += round(decimal.Decimal(0.95) * proposal.proposed_amount, 1)
    active_proposals = BrandProposal.objects.filter(creator=creator , proposal_status = BrandProposal.Proposal_Status.PAID)
    links={}
    if active_proposals.exists():
        links['active_proposals'] = {
                'url': reverse("creator_active_proposals" , kwargs={"creator_id":creator.id}),
                'name': "Active Proposals"
        }
    #shows manage integrations link in navbar only if dashboard exists
    dashboard = InstagramAccountDashBoard.objects.filter(creator = creator)
    if dashboard.exists():
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

def brand_proposal_payment(request , proposal_id):
    proposal = get_object_or_404(BrandProposal , id = proposal_id)

    if proposal.brand.user != request.user :
        raise PermissionDenied

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
    if proposal.brand.user != request.user :
        raise PermissionDenied
    proposal.proposal_status = BrandProposal.Proposal_Status.PAID
    proposal.date_paid = timezone.now()
    proposal.save()
    proposed_date = proposal.date_paid + datetime.timedelta(days = proposal.timeline)
    proposal.duration_left = proposed_date - timezone.now()
    proposal.save()
    
    return render(request , 'base/successfull_payment.html')

def payment_failed(request , brand_id):
    brand = get_object_or_404(BrandProfile , id=brand_id) 
    if brand.user != request.user :
        raise PermissionDenied

    context = {
        'brand_id':brand_id
    }
    
    return render(request , 'base/payment_failed.html', context)
    

def content_approval_process(request, proposal_id):
    transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    creator = get_object_or_404(CreatorProfile, user=request.user)
    proposal = get_object_or_404(BrandProposal, id=proposal_id)
    if proposal.creator != creator:
        raise PermissionDenied
    
    if request.method == 'POST':
        media = request.FILES.getlist("media")
        # Sending using Brevo Email API
        
        template_id = 7
        # Ensure this is uncommented if needed
        approve_url = request.build_absolute_uri(reverse("approve_content", kwargs={"proposal_id": proposal.id}))

    
        to = [{"email": proposal.brand.email}]
        
        files = len(media)
        for i in range(files):
            img = media[i].read()
            payload['image'] = base64.b64encode(img).decode('utf-8')
            response = requests.post(imgbb_url, data=payload)
            
            print(f"Response status code: {response.status_code}")
            json_response = response.json()

            if response.status_code == 200:
                img_url = json_response['data']['url']
                Content_Approval_Images.objects.create(
                    proposal = proposal,
                    url = img_url
                )
            else:
                print("Error uploading image to imgbb:", json_response)
                messages.add_message(request, messages.ERROR, "Error uploading image to Server")
                return redirect(reverse("creator_active_proposals", kwargs={"creator_id": creator.id}))


        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
        )

        try:
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
        except ApiException as e:
            print(f"Error: {e}")
            messages.add_message(request, messages.ERROR, f"Content Approval Email Error: {e}")
        else:
            proposal.proposal_status = BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING
            proposal.save()           
        return redirect(reverse("creator_active_proposals", kwargs={"creator_id": creator.id}))

    else:
        return render(request, 'base/content_approval_form.html')

def brand_pending_approval_view(request):
    brand_profile = get_object_or_404(BrandProfile , user = request.user)
    proposals = BrandProposal.objects.filter(brand = brand_profile , proposal_status = BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING)

    context = {
        "pending_proposals": proposals,
        "account": brand_profile,
    }

    links = {}
    links['your_proposals'] = {
        'url': reverse("brand_proposals" , kwargs={"brand_id":brand_profile.id}),
        'name': "Your Proposals"
    }
    context['links'] = links

    return render(request , 'base/brand_content_approval.html' , context)

def brand_content_review(request , proposal_id):
    approval_content = Content_Approval_Images.objects.filter(proposal__id = proposal_id)
    if approval_content[0].proposal.brand.user != request.user:
        raise PermissionDenied
    
    links = {}
    proposal = get_object_or_404(BrandProposal , id = proposal_id)
    pending_proposals = BrandProposal.objects.filter(brand = proposal.brand , proposal_status=BrandProposal.Proposal_Status.CONTENT_APPROVAL_PENDING)
    your_proposals = BrandProposal.objects.filter(brand=proposal.brand) 
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
        "content": approval_content[0],
        "content_list": approval_content,
        "links": links
    }

    return render(request , 'base/brand_content_review.html' , context) 

def approve_content(request , proposal_id):
    unapproved_content = Content_Approval_Images.objects.filter(proposal__id = proposal_id , verified = False)
    for i in unapproved_content:
        i.verified = True 
        i.save()
    proposal = get_object_or_404(BrandProposal , id=proposal_id)
    proposal.proposal_status = BrandProposal.Proposal_Status.POSTING_CONTENT
    proposal.save()

    transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    template_id = 8

    to = [{"email": proposal.creator.contact_email}]

    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            template_id=template_id,
        )
    
    try:
        api_response = transac_api_instance.send_transac_email(send_smtp_email)
        print("API Response:", api_response)
    except ApiException as e:
        print(f"Error: {e}")
        messages.add_message(request, messages.ERROR, f"Content Approval Email Error: {e}")
    else:
        return render(request , 'base/approved.html')


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
    success_message =  "We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly. If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')

    def form_valid(self, form):
       response = super().form_valid(form)
       try:
        user = EmailUser.objects.get(email=form.cleaned_data['email'])
       except EmailUser.DoesNotExist:
        # Optionally handle the case where the email doesn't exist
        messages.error(self.request, "No account found with this email address.")
        return response
       
       token = default_token_generator.make_token(user)
       uid = urlsafe_base64_encode(force_bytes(user.pk))

       self.send_mail(
           to_email=form.cleaned_data['email'],
           context={'uid': uid, 'token': token},
       )
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
            'code_challenge_method': 'S256'
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
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
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
    creator_profile = get_object_or_404(user = request.user)
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
    if user_data.status_code != 200:
        return JsonResponse({"error": "Failed to get user info", "details": user_data.text}, status=400)

    try:
        user_data_json = user_data.json()
    except ValueError:
        return JsonResponse({"error": "Invalid JSON response", "details": user_data.text}, status=400)

    if user_data_json.get('error', {}).get('code') != 'ok':
        return JsonResponse({
            "error": "Error in TikTok API response",
            "details": user_data_json.get('error', {})
        }, status=400)
    
    # Finding if error exists in tiktok api response
    user_info = user_data_json.get('data', {}).get('user', {})

    user_info_error = user_data_json.get('error')
    if user_info_error == "Failed to get user info":
        
        if "details" in user_data_json:
            try:
                details = json.loads(user_data_json["details"])  # Parse the nested JSON string
                if details.get("error", {}).get("code") == "access_token_invalid":
                    if refresh_token:
                        payload = {
                        'client_key': TIKTOK_CLIENT_KEY,
                        'client_secret': TIKTOK_CLIENT_SECRET,
                        'refresh_token': refresh_token,
                        'grant_type': 'authorization_code'
                        }
                        access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"
                        response = requests.get(access_token_url , data=payload)
                        if response.status_code == 200:
                            refreshed_access_token = response.json().get("access_token")
                            refreshed_refresh_token = response.json().get("refresh_token")
                            if refreshed_access_token is None or refreshed_refresh_token is None:
                                return HttpResponse("API Critical Error : Access Token Not Found !!")
                            else:
                                tiktok_dash.access_token ==  refreshed_access_token
                                tiktok_dash.refresh_token ==  refreshed_refresh_token
                                tiktok_dash.save()
                        else:
                            return JsonResponse({"error": "Not able to Refresh Access token "} , status=response.status_code)
            
            except json.JSONDecodeError:
                return HttpResponse("JSONDECODE ERROR : Failed to parse 'details' field. ")
        
    
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
    tiktok_dash.engagement_rate = decimal.Decimal((tiktok_dash.likes_count/tiktok_dash.follower_count)*100)
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

    