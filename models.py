import hashlib
import os
import unicodedata
from datetime import date
from django.db import models
from django.utils import timezone


class CandidateCreateException(Exception):
    pass

class KeywordException(Exception):
    pass

class CommitteeMemberException(Exception):
    pass

class ThesisException(Exception):
    pass


class Year(models.Model):

    year = models.CharField(max_length=5, unique=True)

    def __unicode__(self):
        return self.year


class Department(models.Model):

    name = models.CharField(max_length=190, unique=True)

    def __unicode__(self):
        return self.name


class Degree(models.Model):

    abbreviation = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=190, unique=True)

    def __unicode__(self):
        return self.abbreviation


class Person(models.Model):

    netid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    last_name = models.CharField(max_length=190)
    first_name = models.CharField(max_length=190)
    middle = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    address_street = models.CharField(max_length=190, blank=True)
    address_city = models.CharField(max_length=190, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        if self.netid == u'':
            self.netid = None
        if self.orcid == u'':
            self.orcid = None
        super(Person, self).save(*args, **kwargs)


class GradschoolChecklist(models.Model):

    dissertation_fee = models.DateTimeField(null=True, blank=True)
    bursar_receipt = models.DateTimeField(null=True, blank=True)
    gradschool_exit_survey = models.DateTimeField(null=True, blank=True)
    earned_docs_survey = models.DateTimeField(null=True, blank=True)
    pages_submitted_to_gradschool = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'%s Checklist' % self.candidate

    def status(self):
        if self.complete():
            return 'Complete'
        else:
            return 'Incomplete'

    def complete(self):
        if self.dissertation_fee and self.bursar_receipt and self.gradschool_exit_survey\
                and self.earned_docs_survey and self.pages_submitted_to_gradschool:
            return True
        else:
            return False


class Language(models.Model):

    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.code


class Keyword(models.Model):

    text = models.CharField(max_length=190, unique=True)
    search_text = models.CharField(max_length=190, blank=True)
    authority = models.CharField(max_length=100, blank=True)
    authority_uri = models.CharField(max_length=190, blank=True)
    value_uri = models.CharField(max_length=190, blank=True)

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if (self.text is None) or (len(self.text) == 0):
            raise KeywordException('no empty keywords allowed')
        self.text = Keyword.normalize_text(self.text)
        if len(self.text) > 190:
            raise KeywordException('keyword %s too long' % self.text.encode('utf8'))
        self.search_text = Keyword.get_search_text(self.text)
        super(Keyword, self).save(*args, **kwargs)

    @staticmethod
    def normalize_text(text):
        '''Normalize the unicode text, so that we don't get multiple entries in the db
        that look exactly the same, but are still allowed because the characters are different'''
        return unicodedata.normalize('NFD', text)

    @staticmethod
    def get_search_text(nfd_normalized_text):
        return u''.join([c for c in nfd_normalized_text if unicodedata.category(c) != 'Mn']).lower()


class Thesis(models.Model):
    '''Represents the actual thesis document that a candidate uploads.
    For the thesis, we track the file name, the checksum, and metadata
    such as title, abstract, keywords, and language.'''
    STATUS_CHOICES = (
            ('not_submitted', 'Not Submitted'),
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        )

    document = models.FileField()
    file_name = models.CharField(max_length=190)
    checksum = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.ManyToManyField(Keyword)
    language = models.ForeignKey(Language, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='not_submitted')
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    date_rejected = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = u'Theses'

    @staticmethod
    def calculate_checksum(thesis_file):
        return hashlib.sha1(thesis_file.read()).hexdigest()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.document:
            if not self.document.name.endswith('pdf'):
                raise ThesisException('must be a pdf file')
            if not self.file_name:
                self.file_name = os.path.basename(self.document.name) #grabbing name from tmp file, since we haven't saved yet
            if not self.checksum:
                self.checksum = Thesis.calculate_checksum(self.document)
        super(Thesis, self).save(*args, **kwargs)

    def update_thesis_file(self, thesis_file):
        self.document = thesis_file
        self.file_name = thesis_file.name
        self.checksum = Thesis.calculate_checksum(self.document)
        self.save()

    def metadata_complete(self):
        if self.title and self.abstract and self.keywords:
            return True
        else:
            return False

    def submit(self):
        if not self.document:
            raise ThesisException('can\'t submit thesis: no document has been uploaded')
        if not self.metadata_complete():
            raise ThesisException('can\'t submit thesis: metadata incomplete')
        self.status = 'pending'
        self.date_submitted = timezone.now()
        self.save()

    def accept(self):
        if self.status != 'pending':
            raise ThesisException('can only accept theses with a "pending" status')
        self.status = 'accepted'
        self.save()

    def reject(self):
        if self.status != 'pending':
            raise ThesisException('can only reject theses with a "pending" status')
        self.status = 'rejected'
        self.save()


class Candidate(models.Model):
    '''Represents a candidate for a degree. Each candidate has a degree that they're
    pursuing, a department that will grant the degree, and a year they're graduating.
    Optionally, a candidate can choose to embargo their thesis for two years.'''

    person = models.ForeignKey(Person)
    date_registered = models.DateField(default=date.today)
    year = models.ForeignKey(Year)
    department = models.ForeignKey(Department)
    degree = models.ForeignKey(Degree)
    embargo_end_year = models.CharField(max_length=4, null=True, blank=True)
    thesis = models.ForeignKey(Thesis, null=True, blank=True)
    gradschool_checklist = models.ForeignKey(GradschoolChecklist, null=True, blank=True) #temporary - should be required
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.person, self.year)

    def save(self, *args, **kwargs):
        if not self.person.netid:
            raise CandidateCreateException('candidate must have a Brown netid')
        if not self.thesis:
            self.thesis = Thesis.objects.create()
        if not self.gradschool_checklist:
            self.gradschool_checklist = GradschoolChecklist.objects.create()
        super(Candidate, self).save(*args, **kwargs)

    @staticmethod
    def get_candidates_by_status(status):
        if status == 'all':
            return Candidate.objects.all()
        elif status == 'in_progress': #dissertation not submitted yet
            return Candidate.objects.filter(thesis__status='not_submitted')
        elif status == 'awaiting_gradschool': #dissertation submitted, needs to be checked by grad school
            return Candidate.objects.filter(thesis__status='pending')
        elif status == 'dissertation_rejected': #dissertation needs to be resubmitted
            return Candidate.objects.filter(thesis__status='rejected')
        elif status == 'paperwork_incomplete': #dissertation approved, still need paperwork
            return [c for c in Candidate.objects.filter(thesis__status='accepted') if not c.gradschool_checklist.complete()]
        elif status == 'complete': #dissertation approved, paperwork complete - everything done
            return [c for c in Candidate.objects.filter(thesis__status='accepted') if c.gradschool_checklist.complete()]


class CommitteeMember(models.Model):
    MEMBER_ROLES = (
            (u'reader', u'Reader'),
            (u'director', u'Director'),
        )

    person = models.ForeignKey(Person)
    role = models.CharField(max_length=25, choices=MEMBER_ROLES, default=u'reader')
    department = models.ForeignKey(Department, null=True, blank=True)
    affiliation = models.CharField(max_length=190, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.person, self.role)

    def save(self, *args, **kwargs):
        if not self.department and not self.affiliation:
            raise CommitteeMemberException('either department or affiliation are required')
        super(CommitteeMember, self).save(*args, **kwargs)
