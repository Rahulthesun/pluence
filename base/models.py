from django.db import models
from users.models import EmailUser

# Create your models here.

class CreatorProfile(models.Model):
    user = models.OneToOneField(EmailUser , on_delete=models.CASCADE)
    name = models.CharField(max_length=200 , null=True , blank=True)
    contact_email = models.EmailField(max_length=200 , null=True , blank=True)
    website = models.URLField(max_length=60 , null=True , blank=True)
    bio = models.TextField(null=True , blank=True)


    active = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email.split('@')[0]} - Creator Profile "
    
class BrandProfile(models.Model):
    user = models.OneToOneField(EmailUser , on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=200 , null=True , blank=False)
    email = models.EmailField(max_length=60 , null=True , blank=False)
    
    about = models.TextField(null=True , blank=True)

    active = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email.split('@')[0]} - Brand Profile "
    

class BrandProposal(models.Model):
    brand = models.ForeignKey(BrandProfile , on_delete= models.SET_NULL , null = True)
    creator = models.ForeignKey(CreatorProfile , on_delete= models.SET_NULL , null=True)
    
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
        COMPLETED ='Completed'

    proposal_status = models.CharField(max_length=200 , choices=Proposal_Status.choices , null = True , blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    duration_left = models.DurationField(null=True , blank=True)

    date_completed = models.DateTimeField(null=True , blank=True)

    def __str__(self):
        return f"{self.brand.user.email.split('@')[0]} - {self.creator.user.email.split('@')[0]}"
    
    
class InstagramAccountDashBoard(models.Model):
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

    def __str__(self):
        return f"{self.username} - IG Account"

    

