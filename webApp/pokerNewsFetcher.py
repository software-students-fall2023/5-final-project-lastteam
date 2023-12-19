import feedparser


def get_poker_news():
    try:
        feed = feedparser.parse('https://news.google.com/rss/search?q=poker&hl=en-US&gl=US&ceid=US:en')
        return feed.entries
    except Exception as e:
        print('Error fetching poker news:', e)
        raise
