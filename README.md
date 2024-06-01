# Linklytics

Linkedin's analytics sucks. A lot. So I've built a small tool that gets some more valuable information out of the raw data they let you download.

> **Note:** I believe you can only download your data if you're in "creator" mode.

## Getting Your Linkedin Analytics Data

1. Go to your Linkedin profile page e.g: https://www.linkedin.com/in/marcelmarais1/
2. Click on the "Show all analytics" button
3. Click on the "Post impressions" buttons.
4. Click the dropdown menu and change "Past 7 days" to what's appropriate for you (I just use "Past 365 days")
5. Click the "Export" button to download your data.

## Running the Tool

1. Install dependencies with Poetry:

```bash
poetry install
```

1. Create a folder in `/linklytics` called `data` and put your downloaded data (`*.xlsx`) in there.
2. Run the tool with:

```bash
poetry run python linklytics/main.py
```

After a while should see an markdown file in `/linklytics/output` with the generated analytics.