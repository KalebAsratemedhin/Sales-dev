import scrapy


class LeadItem(scrapy.Item):
    """One lead from engagement; compatible with POST /api/leads/."""
    email = scrapy.Field()
    name = scrapy.Field()
    company_name = scrapy.Field()
    company_website = scrapy.Field()
    source = scrapy.Field()
    profile_url = scrapy.Field()
    interaction_type = scrapy.Field()  # comment | like | follow | connect
