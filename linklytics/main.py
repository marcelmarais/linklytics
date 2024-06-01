import os

import pandas as pd
from config import config
from models.linkedin_models import LinkedinSheetTypes, validate_linkedin_sheets
from post_scraper import enrich_raw_linkedin_posts, parse_top_posts_df


def get_xlsx_file_name_from_folder(folder_path: str) -> str:
    """Returns the name of the first xlsx file in a given folder"""
    files = os.listdir(folder_path)
    return files[0]


file_name = get_xlsx_file_name_from_folder(config.analytics_path)
linkedin_analytics_xlsx = pd.ExcelFile(config.analytics_path + "/" + file_name)
sheet_names = linkedin_analytics_xlsx.sheet_names
validate_linkedin_sheets(sheet_names)


engagement_sheet = linkedin_analytics_xlsx.parse(LinkedinSheetTypes.ENGAGEMENT.value)
top_posts_df = linkedin_analytics_xlsx.parse(
    LinkedinSheetTypes.TOP_POSTS.value, skiprows=2
)


raw_linkedin_posts = parse_top_posts_df(posts_df=top_posts_df)
raw_linkedin_posts.sort_by_engagements()

top_n = 2

linkedin_posts = enrich_raw_linkedin_posts(
    raw_linkedin_posts=raw_linkedin_posts, top_n=top_n
)

markdown = f"# Linkedin Analytics for: {file_name}\n\n"

markdown += f"## Summary of top {top_n} posts\n"
markdown += f"- **Average post count**: {linkedin_posts.get_avg_word_count()}\n"
markdown += f"- **Average post line count**: {linkedin_posts.get_avg_line_count()}\n"
markdown += (
    f"- **Average hook word count**: {linkedin_posts.get_avg_hook_word_count()}\n"
)

markdown += "## Individual posts\n"
for post in linkedin_posts.posts:
    markdown += f"### Post on {post.publish_date.strftime('%B %d, %Y')} ({post.publish_date.strftime('%A')})\n"
    markdown += f"- **Engagements**: {post.engagements}\n"
    markdown += f"- **Word count**: {post.word_count}\n"
    markdown += f"- **Hook**: {post.hook_str}\n"
    markdown += f"- **Post URL**: [{post.post_url}]({post.post_url})\n"
    markdown += f"– **Line count**: {post.line_count}\n"
    markdown += f"- **Post description**: {post.post_description}\n"

with open(f"output/{file_name.split('.')[0]}.md", "w") as f:
    f.write(markdown)
