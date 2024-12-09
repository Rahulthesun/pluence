from django.contrib import admin
from .models import CreatorProfile , BrandProfile , BrandDeal , InstagramAccountDashBoard , Content_Approval_Media , VerifyEmail
from .models import TiktokDashboard , UnsentEmails
# Register your models here.

admin.site.register(CreatorProfile)
admin.site.register(BrandProfile)
admin.site.register(BrandDeal)
admin.site.register(InstagramAccountDashBoard)
admin.site.register(Content_Approval_Media)
admin.site.register(VerifyEmail)
admin.site.register(TiktokDashboard)
admin.site.register(UnsentEmails)
