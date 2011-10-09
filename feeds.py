from django.contrib.syndication.feeds import Feed
from models import Entry
import datetime

class WeblogEntryFeed(Feed):
    title = "John Moylan's 8t8 weblog"
    link = "/"
    description = "www.8t8.eu/"
    
    def items(self):
        return Entry.live.filter(pub_date__lte=datetime.datetime.now())[:10]

    def item_pubdate(self, item):
        return item.pub_date
