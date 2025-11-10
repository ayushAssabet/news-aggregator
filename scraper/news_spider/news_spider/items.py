import scrapy
class ArticleItem(scrapy.Item):
    title=scrapy.Field(); url=scrapy.Field(); summary=scrapy.Field(); content=scrapy.Field(); author=scrapy.Field(); published_at=scrapy.Field()
