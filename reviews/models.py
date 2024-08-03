from django.db import models

class Brand(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    industry=models.CharField(max_length=50)
    phoneno=models.CharField(max_length=50,null=True)

class Creator(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    platform=models.CharField(max_length=50)
    phoneno=models.CharField(max_length=50)
class Proposal(models.Model):
   Brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
   Creator=models.ForeignKey(Creator,on_delete=models.CASCADE)
   creator_offer=models.DecimalField(max_digits=10,decimal_places=2)
   brand_offer=models.DecimalField(max_digits=10,decimal_places=2)


   