import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup
from metrics import count_lines, count_words, get_hook
from models.linkedin_models import (
    LinkedinPost,
    LinkedinPosts,
    RawLinkedinPost,
    RawLinkedinPosts,
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

ChromeDriverManager().install()


def get_page_html(url: str) -> BeautifulSoup:
    logger = logging.getLogger("WDM")
    logger.setLevel(logging.WARNING)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(service=ChromeService(), options=options)

    try:
        driver.get(url)
        driver.implicitly_wait(5)
        page_html = driver.page_source
        return BeautifulSoup(page_html, "html.parser")

    finally:
        driver.quit()


def extract_post_details(html: BeautifulSoup) -> Optional[str]:
    post_description = html.find(
        "div", class_="attributed-text-segment-list__container"
    )

    if not post_description:
        return None

    return post_description.text


def parse_top_posts_df(posts_df: pd.DataFrame) -> RawLinkedinPosts:
    """
    Converts a pandas dataframe of posts to a LinkedinPosts object.
    The structure of this dataframe is frankly a bit weird, but it's the way it is.
    Microsoft should be ashamed of themselves.

    args:
        posts_df: A pandas dataframe of posts

    returns:
        A LinkedinPosts object
    """
    raw_linkedin_posts = RawLinkedinPosts()

    for index, row in posts_df.iterrows():
        engagements_published_date = datetime.strptime(
            row["Post publish date"], "%m/%d/%Y"
        )
        engagements = row["Engagements"]
        engagements_post_url = row["Post URL"]
        impressions = row["Impressions"]
        impressions_post_url = row["Post URL.1"]
        impressions_published_date = datetime.strptime(
            row["Post publish date.1"], "%m/%d/%Y"
        )

        impressions_post = RawLinkedinPost(
            post_url=impressions_post_url,
            publish_date=impressions_published_date,
            impressions=impressions,
        )

        engagements_post = RawLinkedinPost(
            post_url=engagements_post_url,
            publish_date=engagements_published_date,
            engagements=engagements,
        )

        raw_linkedin_posts.add_post(impressions_post)
        raw_linkedin_posts.add_post(engagements_post)

    raw_linkedin_posts.sort_by_engagements()

    return raw_linkedin_posts


def enrich_raw_linkedin_posts(
    raw_linkedin_posts: RawLinkedinPosts, top_n: int = 20
) -> LinkedinPosts:
    if top_n > len(raw_linkedin_posts.posts):
        raise ValueError(
            f"The top_n ({top_n}) cannot be greater than the number of posts ({len(raw_linkedin_posts.posts)})"
        )
    linkedin_posts = LinkedinPosts()

    for post in raw_linkedin_posts.posts[:top_n]:
        html = get_page_html(post.post_url)

        post_details = extract_post_details(html)
        if post_details is None:
            continue

        linkedin_posts.add_post(
            LinkedinPost(
                engagements=post.engagements,
                impressions=post.impressions,
                word_count=count_words(post_details),
                line_count=count_lines(post_details),
                post_description=post_details,
                post_url=post.post_url,
                publish_date=post.publish_date,
                hook_str=get_hook(post_details),
                hook_word_count=count_words(get_hook(post_details)),
            )
        )

    return linkedin_posts
