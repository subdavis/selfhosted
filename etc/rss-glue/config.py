from datetime import datetime, timedelta

from rss_glue.feeds import DigestFeed, HackerNewsFeed, RedditFeed
from rss_glue.outputs import Artifact, HTMLIndexOutput, HtmlOutput, OpmlOutput, RssOutput
from rss_glue.resources import global_config

global_config.configure()

selfhosted_reddit_top_feed = RedditFeed(
    "https://www.reddit.com/r/selfhosted/top.json?t=week",
)
weekly_selfhosted = DigestFeed(
    source=selfhosted_reddit_top_feed,
    limit=8,
    schedule="15 6 * * 2",  # Weekly on Tuesdays at 6:15am
)

cyclingmsp_reddit_top_feed = RedditFeed(
    "https://www.reddit.com/r/cyclingmsp/top.json?t=week",
    interval=timedelta(weeks=52),
)
weekly_cyclingmsp = DigestFeed(
    source=cyclingmsp_reddit_top_feed,
    limit=8,
    schedule="30 7 * * 1",  # Weekly on Mondays at 7:30am
)

yc_feed = HackerNewsFeed(feed_type="best")
daily_yc_digest = DigestFeed(
    source=yc_feed,
    limit=10,
    schedule="0 8 * * *",  # Daily at 8:00am
)

artifacts: list[Artifact] = [
    HTMLIndexOutput(
        HtmlOutput(
            weekly_selfhosted,
            weekly_cyclingmsp,
            daily_yc_digest,
        ),
        RssOutput(
            weekly_selfhosted,
            weekly_cyclingmsp,
            daily_yc_digest,
        ),
        OpmlOutput(
            RssOutput(
                weekly_selfhosted,
                weekly_cyclingmsp,
                daily_yc_digest,
            ),
        ),
    ),
]
