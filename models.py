import akismet
import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.signals import comment_was_posted, comment_will_be_posted
from django.utils.encoding import smart_str
from django.core.cache import cache
from tagging.models import Tag
from tagging.fields import TagField
from django.contrib.flatpages.models import FlatPage
from django.db.models.signals import post_save, post_delete
from django.db.models import signals
from django.contrib.comments.models import Comment
from jot import signals


class Category(models.Model):
    title = models.CharField(max_length=250,
                             help_text='Maximum 250 characters.')
    slug = models.SlugField(unique=True,
                            help_text="Suggested value automatically generated from title. Must be unique.")
    description = models.TextField()

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return "/category/%s/" % self.slug

    def live_entry_set(self):
        from models import Entry
        return self.entry_set.filter(status=Entry.LIVE_STATUS)

class LiveEntryManager(models.Manager):
    def get_query_set(self):
        return super(LiveEntryManager, self).get_query_set().filter(status=self.model.LIVE_STATUS)


class Entry(models.Model):
    LIVE_STATUS = 1
    DRAFT_STATUS = 2
    HIDDEN_STATUS = 3
    STATUS_CHOICES = (
        (LIVE_STATUS, 'Live'),
        (DRAFT_STATUS, 'Draft'),
        (HIDDEN_STATUS, 'Hidden'),
        )

    pub_date = models.DateTimeField(verbose_name='Publish Date',
        help_text='Date Entry was published (Defaults to now is left empty)',
        blank=True, null=True, editable=True, default=datetime.datetime.now())
    updated_date = models.DateTimeField(verbose_name='Date last updated',
        help_text='Date Entry was last updated (Defaults to now is left empty)',
        blank=True, null=True, editable=False)
    slug = models.SlugField(max_length=32, unique_for_date='pub_date')
    headline = models.CharField(max_length=255)
    summary = models.TextField(help_text="Use plain text (no HTML).")
    body = models.TextField(help_text="")
    user = models.ForeignKey(User, help_text='Use the full name',)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=LIVE_STATUS,
        help_text=u'Only entries with "live" status will be displayed publicly.')
    # Categorization.
    meta_keywords = models.CharField(blank=True, max_length=300, help_text='Comma-separated list of keyworks for this entry. Maximum 300 characters.')
    meta_description = models.CharField(blank=True, max_length=400, help_text='A brief description of this entry. Maximum 400 characters.')
    tags = TagField(verbose_name=('Tags'), help_text=('Separate tags with spaces or commas.'), blank=False)
    category = models.ManyToManyField(Category, blank=True, verbose_name=("Category"))
    featured = models.BooleanField(default=False)
    comments_allowed = models.BooleanField(default=True)
    # Managers.
    objects = models.Manager()
    live = LiveEntryManager()


    class Meta:
        db_table = 'blog_entries'
        verbose_name_plural = 'entries'
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __unicode__(self):
        return self.headline

    def get_absolute_url(self):
        return "/weblog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)

    def save(self):
        self.updated_date = datetime.datetime.today()
        super(Entry, self).save()


    @property
    def enable_comments(self):
        if self.comments_allowed == False:
            return 0
        else:
            delta = datetime.datetime.now() - self.pub_date
            return delta.days < 60

class Link(models.Model):
    # Metadata.
    enable_comments = models.BooleanField(default=True)
    post_elsewhere = models.BooleanField('Post to Delicious',
                                         default=True,
                                         help_text='If checked, this link will be posted both to your weblog and your del.icio.us account.')
    posted_by = models.ForeignKey(User)
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    slug = models.SlugField(unique_for_date='pub_date',
                            help_text='Must be unique for the publication date.')
    title = models.CharField(max_length=250)

    # The actual link bits.
    description = models.TextField(blank=True)
    via_name = models.CharField('Via', max_length=250, blank=True,
                                help_text='The name of the person whose site you spotted the link on. Optional.')
    via_url = models.URLField('Via URL', blank=True,
                              help_text='The URL of the site where you spotted the link. Optional.')
    tags = TagField()
    url = models.URLField(unique=True)

    class Meta:
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False):
        if not self.id and self.post_elsewhere:
            import pydelicious
            from django.utils.encoding import smart_str
            pydelicious.add(settings.DELICIOUS_USER, settings.DELICIOUS_PASSWORD,
                            smart_str(self.url), smart_str(self.title),
                            smart_str(self.tags))
        #if self.description:
        #    self.description_html = markdown(self.description)
        super(Link, self).save()

    def get_absolute_url(self):

        return ('zeus_link_detail', (), { 'year': self.pub_date.strftime('%Y'),
                                              'month': self.pub_date.strftime('%b').lower(),
                                              'day': self.pub_date.strftime('%d'),
                                              'slug': self.slug })
    get_absolute_url = models.permalink(get_absolute_url)

def comment_handler(sender, **kwargs):
    #if moderation is enabled in the settings file then premoderate messages
    if hasattr(settings, 'PREMODERATE') and settings.PREMODERATE.lower() == 'true':
        comment = kwargs['comment']
        comment.is_public = False
    else:
        return

comment_will_be_posted.connect(comment_handler)


def moderate_comment(sender, comment, request, *args, **kwargs):
    try:
        from akismet import Akismet
    except:
        # TODO: log this "can't find akismet in your Python path"
        return

    # use TypePad's AntiSpam if the key is specified in settings.py
    if hasattr(settings, 'TYPEPAD_ANTISPAM_API_KEY'):
        ak = Akismet(
            key=settings.TYPEPAD_ANTISPAM_API_KEY,
            blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain
        )
        ak.baseurl = 'api.antispam.typepad.com/1.1/'
    elif hasattr(settings, 'AKISMET_API_KEY'):
        ak = Akismet(
            key=settings.AKISMET_API_KEY,
            blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain
        )
    else:
        #"AKISMET_API_KEY required in settings file to use this feature"
        return

    if ak.verify_key():
        data = {
            'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERRER', ''),
            'comment_type': 'comment',
            'comment_author': smart_str(comment.user_name),
        }
        if ak.comment_check(smart_str(comment.comment.encode('utf-8')), data=data, build_data=True):
            comment.flags.create(
                user =comment.content_object.user,
                flag = 'spam'
            )
            comment.is_public = False
            comment.save()
    else:
        #TODO: log this "invalid Akismet key"
        return



comment_was_posted.connect(moderate_comment)

#def update_page_signal(sender, **kwargs):
#    quick_delete('/','/sitemap.xml',kwargs['instance'])


#post_save.connect(signals.delete_blog_index, sender=Entry)
#post_delete.connect(signals.delete_blog_index, sender=Entry)
#post_save.connect(signals.delete_blog_index, sender=Category)
#post_delete.connect(signals.delete_blog_index, sender=Category)

#post_delete.connect(signals.clear_stagnant_cache_on_comment_change, sender=Comment)
#post_save.connect(signals.clear_stagnant_cache_on_comment_change, sender=Comment)

