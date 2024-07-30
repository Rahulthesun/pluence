from django.db import models
from django.contrib.auth.models import BaseUserManager , PermissionsMixin , AbstractBaseUser

# Create your models here.

class EmailUserManager(BaseUserManager):
    def create_user(self , email , password = None):
        if not email:
            raise ValueError("Enter a Valid Email")
        if not password:
            raise ValueError("Your Password is Invalid")
        email = self.normalize_email(email)
        user = self.model(email = email)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email , password=None):
        if not email:
            raise ValueError("Enter a Valid Email")
        if not password:
            raise ValueError("Your Password is Invalid")
        user = self.create_user(email=email , password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

        
class EmailUser(AbstractBaseUser , PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=60 , unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='emailuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='emailuser_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


    objects = EmailUserManager()
    def __str__(self):
        return self.email.split('@')[0]