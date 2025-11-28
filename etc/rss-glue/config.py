import os
from datetime import timedelta

from rss_glue import feeds, resources

ai_client = feeds.ClaudeClient(api_key=os.getenv("ANTHROPIC_KEY", ""), model="claude-haiku-4-5")
scrape_key = os.getenv("INSTA_SC_API_KEY", "")
digest_limit = 8

resources.global_config.configure(base_url="https://rssglue.subdavis.com/", output_limit=6)
# resources.global_config.configure(output_limit=6)

cycling_feeds = [
    *[
        feeds.InstagramFeed(
            username=username,
            api_key=scrape_key,
            interval=timedelta(hours=24),
        )
        for username in [
            "behindbarsbicycleshop",
            "bikingwithbaddies",
            "perennialcycle",
            "bonesawcyclingcollective",
            "fastcasualmpls",
            "versusraceteam",
            "joyfulridersclub",
            "handupracing",
        ]
    ],
    feeds.FacebookGroupFeed(
        origin_url="https://www.facebook.com/groups/UtepilsCycling/",
        title="Utepils Cycling",
        api_key=scrape_key,
        interval=timedelta(hours=24),
    ),
]

hn = feeds.HackerNewsFeed(feed_type="best", interval=timedelta(days=2))

cycling_merge = feeds.MergeFeed(
    "cycling_instagram_merge",
    *cycling_feeds,
    title="Cycling Instagram Merge",
)

apod = feeds.RssFeed(
    "nasa_apod",
    "https://www.nasa.gov/feeds/iotd-feed/",
    interval=timedelta(days=7),
)

all_feeds = [
    hn,
    # Reddit r/selfhosted digest
    feeds.DigestFeed(
        source=feeds.RedditFeed(
            "https://www.reddit.com/r/selfhosted/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 2",  # Weekly on Tuesdays at 6:15am
    ),
    # Reddit r/cyclingmsp digest
    feeds.DigestFeed(
        source=feeds.RedditFeed(
            "https://www.reddit.com/r/cyclingmsp/top.json?t=week",
            interval=timedelta(weeks=52),
        ),
        limit=digest_limit,
        schedule="30 7 * * 1",  # Weekly on Mondays at 7:30am
    ),
    # Reddit r/myog digest
    feeds.DigestFeed(
        source=feeds.RedditFeed(
            "https://www.reddit.com/r/myog/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 3",  # Weekly on Wednesdays at 6:15am
    ),
    # Reddit Ezra Klein digest
    feeds.DigestFeed(
        source=feeds.RedditFeed(
            "https://www.reddit.com/r/ezraklein/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 4",  # Weekly on Thursdays at 6:15am
    ),
    # r/minneapolis digest
    feeds.DigestFeed(
        source=feeds.RedditFeed(
            "https://www.reddit.com/r/minneapolis/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="0 8 * * 5",  # Weekly on Fridays at 8:00am
    ),
    # Hacker News best digest
    feeds.DigestFeed(
        source=hn,
        limit=10,
        schedule="0 8 * * *",  # Daily at 8:00am
    ),
    # Nasa APOD Weekly Digest
    apod,
    feeds.DigestFeed(
        source=apod,
        limit=7,
        schedule="30 9 * * 6",  # Weekly on Saturdays at 9:30am
    ),
    cycling_merge,
    # Digest of merged cycling Instagram feeds
    feeds.DigestFeed(
        source=cycling_merge,
        limit=digest_limit,
        schedule="0 7 * * 2",  # Weekly on Tuesdays at 7:00am
    ),
    *cycling_feeds,
    feeds.AiFilterFeed(
        source=cycling_merge,
        client=feeds.ClaudeClient(api_key=os.getenv("ANTHROPIC_KEY"), model="claude-sonnet-4-5"),
        prompt=(
            "This post is relevant if it describes an event, meetup, or group ride that"
            " is happening in the future and open to the general public.  It is not"
            " relevant if it's about a previous event or any other type of content."
        ),
        limit=5,
        title="Cycling Instagram Event Feed",
    ),
]

sources = [feeds.CacheFeed(feed) for feed in all_feeds]
