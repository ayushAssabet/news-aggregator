import os
BOT_NAME='news_spider'
SPIDER_MODULES=['news_spider.spiders']
NEWSPIDER_MODULE='news_spider.spiders'
ROBOTSTXT_OBEY=True
USER_AGENT=os.getenv('USER_AGENT','news-pipeline-bot/1.0')
DOWNLOAD_DELAY=float(os.getenv('DOWNLOAD_DELAY','1.0'))
CONCURRENT_REQUESTS=int(os.getenv('CONCURRENT_REQUESTS','8'))
ITEM_PIPELINES={'news_spider.pipelines.StoreArticlePipeline':300}
