# Nordic News Radar

Mobile-friendly Swedish news dashboard powered by public RSS feeds.

## Deployment

1. In GitHub repository Settings → Pages, choose **GitHub Actions** as the build and deployment source.
2. Under Actions, manually run **Update news feeds** to fetch the first headlines.
3. Under Actions, run **Publish website** if it has not already started.
4. Visit https://sura34.github.io/nordic-news-radar/ once the Pages deployment succeeds.

The hourly workflow runs approximately hourly, subject to GitHub scheduling delays. Refresh in the website loads the most recent collected data. No AI translation is implemented; news excerpts remain in source languages. Public RSS feed availability and reuse terms vary; the collector tolerates individual feed failures.
