from datetime import datetime, timedelta

from rss_glue.feeds import CacheFeed, DigestFeed, HackerNewsFeed, MergeFeed, RedditFeed, RssFeed
from rss_glue.outputs import Artifact, HTMLIndexOutput, HtmlOutput, OpmlOutput, RssOutput
from rss_glue.resources import global_config

global_config.configure(base_url="https://rssglue.subdavis.com/")
# global_config.configure()

cycling_limit = 5

cycling_feeds = [
    RssFeed(
        "behind_bars_instagram",
        "https://rss.app/feeds/oicb357URm4uKhL4.xml",
        interval=timedelta(minutes=24),
        limit=cycling_limit,
    ),
    RssFeed(
        "biking_with_baddies",
        "https://rss.app/feeds/ChQBUWMjZNihd5CT.xml",
        interval=timedelta(minutes=27),
        limit=cycling_limit,
    ),
    RssFeed(
        "perennial_instagram",
        "https://rss.app/feeds/qh4C9SDdfO2j1Uu9.xml",
        interval=timedelta(minutes=29),
        limit=cycling_limit,
    ),
    RssFeed(
        "bone_saw_instagram",
        "https://rss.app/feeds/Sk5cdDN4jObrm6eB.xml",
        interval=timedelta(minutes=31),
        limit=cycling_limit,
    ),
    RssFeed(
        "fast_casual_instagram",
        "https://rss.app/feeds/KJ2EbycVWNUutfSf.xml",
        interval=timedelta(minutes=26),
        limit=cycling_limit,
    ),
    RssFeed(
        "versus_cycles_instagram",
        "https://rss.app/feeds/nizlLvOeAd0G649l.xml",
        interval=timedelta(minutes=28),
        limit=cycling_limit,
    ),
    RssFeed(
        "joyful_rides_instagram",
        "https://rss.app/feeds/Kq509BvbziDAmPoT.xml",
        interval=timedelta(minutes=30),
        limit=cycling_limit,
    ),
    RssFeed(
        "handup_racing_instagram",
        "https://rss.app/feeds/jSSwBkeL8zSPDpSh.xml",
        interval=timedelta(minutes=32),
        limit=cycling_limit,
    ),
    RssFeed(
        "utepils_facebook",
        "https://rss.app/feeds/wVt5kiZWd4l5jWIq.xml",
        interval=timedelta(minutes=33),
        limit=cycling_limit,
    ),
]

digest_limit = 8
other_feeds = [
    # Reddit r/selfhosted digest
    DigestFeed(
        source=RedditFeed(
            "https://www.reddit.com/r/selfhosted/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 2",  # Weekly on Tuesdays at 6:15am
    ),
    # Reddit r/cyclingmsp digest
    DigestFeed(
        source=RedditFeed(
            "https://www.reddit.com/r/cyclingmsp/top.json?t=week",
            interval=timedelta(weeks=52),
        ),
        limit=digest_limit,
        schedule="15 6 * * 1",  # Weekly on Mondays at 7:30am
    ),
    # Reddit r/myog digest
    DigestFeed(
        source=RedditFeed(
            "https://www.reddit.com/r/myog/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 3",  # Weekly on Wednesdays at 6:15am
    ),
    # Reddit Ezra Klein digest
    DigestFeed(
        source=RedditFeed(
            "https://www.reddit.com/r/ezraklein/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="15 6 * * 4",  # Weekly on Thursdays at 6:15am
    ),
    # r/minneapolis digest
    DigestFeed(
        source=RedditFeed(
            "https://www.reddit.com/r/minneapolis/top.json?t=week",
        ),
        limit=digest_limit,
        schedule="0 8 * * 5",  # Weekly on Fridays at 8:00am
    ),
    # Hacker News best digest
    DigestFeed(
        source=HackerNewsFeed(feed_type="best", interval=timedelta(days=7)),
        limit=10,
        schedule="0 6 * * *",  # Daily at 6:00am
    ),
    # Nasa APOD Weekly Digest
    DigestFeed(
        source=RssFeed(
            "nasa_apod",
            "https://www.nasa.gov/feeds/iotd-feed/",
            interval=timedelta(days=7),
        ),
        limit=7,
        schedule="30 9 * * 6",  # Weekly on Saturdays at 9:30am
    ),
    MergeFeed(
        "cycling_instagram_merge",
        *cycling_feeds,
        title="Cycling Instagram Merge",
    ),
]

feeds = [*other_feeds, *cycling_feeds]
feeds = [CacheFeed(feed) for feed in feeds]

artifacts: list[Artifact] = [
    HTMLIndexOutput(
        HtmlOutput(*feeds),
        RssOutput(*feeds),
        OpmlOutput(
            RssOutput(*feeds),
        ),
    ),
]
