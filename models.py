from django.db import models


class Year(models.Model):

    year = models.CharField(max_length=5, unique=True)


class Department(models.Model):

    name = models.CharField(max_length=190, unique=True)


class Person(models.Model):

    netid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    last_name = models.CharField(max_length=190)
    first_name = models.CharField(max_length=190)
    middle = models.CharField(max_length=100)
    email = models.EmailField()
    address_street = models.CharField(max_length=190)
    address_city = models.CharField(max_length=190)
    address_state = models.CharField(max_length=2)
    address_zip = models.CharField(max_length=20)
    phone = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.netid == u'':
            self.netid = None
        if self.orcid == u'':
            self.orcid = None
        super(Person, self).save(*args, **kwargs)
