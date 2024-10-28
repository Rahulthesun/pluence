from django.db import models
from users.models import EmailUser
import random
from django.utils import timezone
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = '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'
transac_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Create your models here.

class CreatorProfile(models.Model):

    referral_code = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10].upper())
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)


    user = models.OneToOneField(EmailUser , on_delete=models.CASCADE)
    name = models.CharField(max_length=200 , null=True , blank=True)
    contact_email = models.EmailField(max_length=200 , null=True , blank=False , unique=True)
    website = models.URLField(max_length=60 , null=True , blank=True)
    bio = models.TextField(null=True , blank=True)

    balance= models.DecimalField(default=0 , decimal_places=2 , max_digits=10 , blank=False)

    active = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email.split('@')[0]} - Creator Profile"
    
class VerifyEmail(models.Model):
    email = models.EmailField(max_length=60 , null=False , blank= False)
    class AccountType(models.TextChoices):
        CREATOR='Creator'
        BRAND='BRAND'

    account_type = models.CharField(max_length=100 , choices=AccountType.choices , null=False , blank=False)
    
    verification_code = models.CharField(max_length=200 ,null=True , blank=True)
    code_sent_at = models.DateTimeField(null=True , blank=True)

    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}-{self.verified}"

    def generate_verification_code(self):
        self.verification_code = "".join(random.choices("0123456789", k=4))
        self.code_sent_at = timezone.now()
        self.save()

    def send_verification_email(self):
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
            api_response = transac_api_instance.send_transac_email(send_smtp_email)
            print("API Response:", api_response)
        except ApiException as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        else:       
            return True
        
class BrandProfile(models.Model):
    user = models.OneToOneField(EmailUser , on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=200 , null=True , blank=True)
    email = models.EmailField(max_length=60 , null=True , blank=False , unique=True)
    
    about = models.TextField(null=True , blank=True)

    subscription_months = models.IntegerField(default=1)

    subscription_active = models.BooleanField(default=False)
    subscribed_date = models.DateTimeField(null=True , blank=True)
        
    subscription_expiry_date = models.DateTimeField(null=True , blank=True)
    subscription_expiry_duration = models.DurationField(null=True , blank=True)
    
    
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email.split('@')[0]} -{self.brand_name} Brand "

class InstagramAccountDashBoard(models.Model):
    dashboard_img = models.URLField(null=True , blank=False)
    creator = models.OneToOneField(CreatorProfile , on_delete=models.CASCADE)
    username = models.CharField(max_length=200 , null=True , blank = False)
    tags = models.TextField(null=True , blank=False)
    followers = models.IntegerField(null= True , blank=False)
    reach = models.IntegerField(null=True , blank=False)
    profile_link_clicks = models.IntegerField(null=True , blank=True)
    engagement = models.IntegerField(null=True , blank=False)

    class Countries(models.TextChoices):
        NONE = "None"
        UNITED_STATES = 'United States'
        CANADA = 'Canada'
        UNITED_KINGDOM = 'United Kingdom'
        AUSTRALIA = 'Australia'
        INDIA = 'India'
        BRAZIL = 'Brazil'
        GERMANY = 'Germany'
        FRANCE = 'France'
        ITALY = 'Italy'
        SPAIN = 'Spain'
        JAPAN = 'Japan'
        SOUTH_KOREA = 'South Korea'
        CHINA = 'China'
        RUSSIA = 'Russia'
        MEXICO = 'Mexico'
        ARGENTINA = 'Argentina'
        SOUTH_AFRICA = 'South Africa'
        INDONESIA = 'Indonesia'
        TURKEY = 'Turkey'
        SAUDI_ARABIA = 'Saudi Arabia'
        UNITED_ARAB_EMIRATES = 'United Arab Emirates'
        NETHERLANDS = 'Netherlands'
        SWEDEN = 'Sweden'
        SWITZERLAND = 'Switzerland'
        BELGIUM = 'Belgium'
        POLAND = 'Poland'
        NORWAY = 'Norway'
        DENMARK = 'Denmark'
        FINLAND = 'Finland'
        PORTUGAL = 'Portugal'
        GREECE = 'Greece'
        IRELAND = 'Ireland'
        NEW_ZEALAND = 'New Zealand'
        MALAYSIA = 'Malaysia'
        PHILIPPINES = 'Philippines'
        THAILAND = 'Thailand'
        VIETNAM = 'Vietnam'
        SINGAPORE = 'Singapore'
        HONG_KONG = 'Hong Kong'
        EGYPT = 'Egypt'
        NIGERIA = 'Nigeria'
        KENYA = 'Kenya'
        ISRAEL = 'Israel'
        COLOMBIA = 'Colombia'
        PERU = 'Peru'
        CHILE = 'Chile'
        PAKISTAN = 'Pakistan'
        BANGLADESH = 'Bangladesh'
        UKRAINE = 'Ukraine'
        ROMANIA = 'Romania'
        HUNGARY = 'Hungary'
        CZECH_REPUBLIC = 'Czech Republic'
        AUSTRIA = 'Austria'

    #audience_data
    audience_country = models.CharField(max_length = 100 ,choices=Countries.choices , blank=False , default=Countries.NONE)
    #audience_age = models.CharField(max_length=100)

    #rates
    story_rates = models.DecimalField(default=0 , decimal_places=2 , max_digits=10 , blank=True)
    reel_rates = models.DecimalField(default=0 , decimal_places=2 , max_digits=10 ,blank=True)
    
    average_rate = models.DecimalField(default=0 , decimal_places=2 , max_digits=10)

    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.username} - IG Account"

class BrandProposal(models.Model):
    brand = models.ForeignKey(BrandProfile , on_delete= models.CASCADE , null = True)
    creator = models.ForeignKey(CreatorProfile , on_delete= models.CASCADE , null=True)
    account = models.OneToOneField(InstagramAccountDashBoard ,on_delete= models.SET_NULL , null=True)

    description = models.TextField(null=True , blank=True)
    timeline = models.IntegerField(default=3 , blank=False)
    proposed_amount = models.DecimalField(default=0 , decimal_places=2 , max_digits=10 , blank=False)
    item_link = models.URLField(null=True , blank=True)

    class Content_Choices(models.TextChoices):
        REELS = 'Reels'
        STORY = 'Story'
        POST = 'Post'
        ALL = 'Reels + Post + Story'

    content_type = models.CharField(max_length=200 , null=False , blank = False ,choices=Content_Choices.choices , default=Content_Choices.ALL)
    
    class Proposal_Status(models.TextChoices):
        REQUESTED = 'Requested'
        REJECTED = 'Rejected'
        ACCEPTED = 'Accepted'
        PAID = 'Paid'
        CONTENT_APPROVAL_PENDING = 'Content Approval Pending'
        POSTING_CONTENT = 'Posting Content'
        COMPLETED ='Completed'

    proposal_status = models.CharField(max_length=200 , choices=Proposal_Status.choices , null = True , blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    date_paid = models.DateTimeField(null=True , blank=True)

    duration_left = models.DurationField(null=True , blank=True)

    date_completed = models.DateTimeField(null=True , blank=True)

    def __str__(self):
        brand_user_email = self.brand.user.email.split('@')[0] if self.brand and self.brand.user else "No Brand"
        creator_user_email = self.creator.user.email.split('@')[0] if self.creator and self.creator.user else "No Creator"
        return f"{brand_user_email} - {creator_user_email} - {self.id}"

class Content_Approval_Images(models.Model):
    proposal = models.ForeignKey(BrandProposal , on_delete=models.CASCADE)
    url = models.URLField(null=True)
    verified = models.BooleanField(default=False)

class Referral(models.Model):
    referrer = models.ForeignKey(CreatorProfile, related_name="referrals", on_delete=models.CASCADE)
    referred = models.OneToOneField(CreatorProfile, related_name="referred_by", on_delete=models.CASCADE, null=True, blank=True)
    referred_email = models.EmailField(max_length=200)
    referral_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.user.email} referred {self.referred_email}"

    

