from django.contrib.syndication.feeds import Feed
from blog.models import Entry
import datetime

class WeblogEntryFeed(Feed):
    title = "John Moylan's 8t8 weblog"
    link = "/weblog/"
    description = "www.8t8.eu/weblog/"
    
    def items(self):
        return Entry.live.filter(pub_date__lte=datetime.datetime.now())[:10]

    def item_pubdate(self, item):
        return item.pub_date
