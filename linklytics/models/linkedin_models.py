import datetime
import logging
from enum import Enum
from typing import Counter, List, Optional, Tuple

import nltk
from nltk.corpus import stopwords
from pydantic import BaseModel

nltk.download("stopwords")


class LinkedinSheetTypes(Enum):
    ENGAGEMENT = "ENGAGEMENT"
    TOP_POSTS = "TOP POSTS"
    DISCOVERY = "DISCOVERY"
    FOLLOWERS = "FOLLOWERS"
    DEMOGRAPHICS = "DEMOGRAPHICS"


def validate_linkedin_sheets(sheet_names: List[str | int]):
    sheet_name_cleaned = [str(sheet_name) for sheet_name in sheet_names]
    for sheet_name in sheet_name_cleaned:
        if any(sheet_name == item.value for item in LinkedinSheetTypes):
            continue

        logging.error(
            f"The sheet name {sheet_name} does not appear in the enum {LinkedinSheetTypes.__members__}.\n"
            "Exiting..."
        )
        exit(1)


class RawLinkedinPost(BaseModel):
    publish_date: datetime.datetime
    post_url: str
    engagements: Optional[int] = None
    impressions: Optional[int] = None

    def __str__(self) -> str:
        return f"Post URL: {self.post_url}, Publish Date: {self.publish_date}, Engagements: {self.engagements}, Impressions: {self.impressions}"


class RawLinkedinPosts(BaseModel):
    posts: List[RawLinkedinPost] = []

    def get_post_by_url(self, url: str) -> Optional[RawLinkedinPost]:
        for post in self.posts:
            if post.post_url == url:
                return post
        return None

    def add_post(self, post: RawLinkedinPost):
        existing_post = self.get_post_by_url(post.post_url)
        if existing_post and post.engagements:
            existing_post.engagements = post.engagements
            return
        if existing_post and post.impressions:
            existing_post.impressions = post.impressions
            return

        self.posts.append(post)

    def __str__(self) -> str:
        return "\n".join([str(post) for post in self.posts])

    def sort_by_engagements(self):
        self.posts.sort(
            key=lambda post: post.engagements if post.engagements else 0, reverse=True
        )


class LinkedinPost(RawLinkedinPost):
    post_description: str
    word_count: int
    line_count: int
    hook_str: str
    hook_word_count: int


class LinkedinPosts(BaseModel):
    posts: List[LinkedinPost] = []

    def get_avg_word_count(self) -> float:
        return sum([post.word_count for post in self.posts]) / len(self.posts)

    def get_avg_line_count(self) -> float:
        return sum([post.line_count for post in self.posts]) / len(self.posts)

    def add_post(self, post: LinkedinPost):
        self.posts.append(post)

    def get_avg_hook_word_count(self) -> float:
        return sum([post.hook_word_count for post in self.posts]) / len(self.posts)

    def most_popular_words_in_hook(self) -> List[Tuple[str, int]]:
        hook_words: List[str] = []
        for post in self.posts:
            hook_words.extend(post.hook_str.lower().split())

        # Remove stop words
        stop_words = set(stopwords.words("english"))
        hook_words = [word for word in hook_words if word not in stop_words]

        hook_counter = Counter(hook_words)

        return hook_counter.most_common(5)
