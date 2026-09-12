from gdo.base.GDO_Module import GDO_Module
from gdo.base.Application import Application
from gdo.core.GDT_Bool import GDT_Bool
from gdo.date.GDT_Duration import GDT_Duration

from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer
from gdo.irc_spider.Spider import Spider


class module_irc_spider(GDO_Module):
    """Consent-aware IRC network discovery controlled by staff."""

    def gdo_dependencies(self):
        return ['irc']

    def gdo_module_config(self):
        return [
            GDT_Bool('irc_spider_enabled').not_null().initial('0'),
            GDT_Duration('irc_spider_cooldown').not_null().initial('5m').min(60),
            GDT_Duration('irc_spider_intro_timeout').not_null().initial('42m').min(60),
        ]

    def gdo_classes(self):
        return [GDO_SpiderServer, GDO_SpiderChannel]

    def gdo_init(self):
        Application.EVENTS.add_timer_async(60, self.on_timer, repeat=2_000_000_000)

    async def on_timer(self):
        if not self.get_config_value('irc_spider_enabled'):
            return
        await Spider.on_timer()
        from gdo.irc_spider.method.spider_channel import spider_channel
        await spider_channel.on_timer()

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe('irc_list_entry', Spider.on_list_entry)
        Application.EVENTS.subscribe('irc_list_finished', Spider.on_list_finished)
        Application.EVENTS.subscribe('irc_bot_kicked', Spider.on_bot_kicked)
        Application.EVENTS.subscribe('bot_joined_channel', Spider.on_bot_joined)
