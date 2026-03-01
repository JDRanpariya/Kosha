# test_rss.py
from connectors.newsletters.rss import RssNewsletterConnector

# Paul Graham's essay feed is a great, simple RSS feed to test with
config = {"feed_url": "https://filipesilva.github.io/paulgraham-rss/feed.rss"}

connector = RssNewsletterConnector(config)
results = connector.fetch()

print(f"Found {len(results)} articles!")
if results:
    first_item = results[0]
    print(f"\nTitle: {first_item.title}")
    print(f"URL: {first_item.url}")
    print(f"Published: {first_item.published_at}")
    print(f"\nPreview of Content:\n{first_item.content[:200]}...")
