from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer
from gdo.irc_spider.Spider import Spider


class spider_channel(Method):
    """Queue a random unvisited channel from the selected Spider server."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'spider.channel'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return []

    @classmethod
    async def on_timer(cls):
        active = GDO_SpiderServer.active()
        if not active:
            return False
        state = active[0]
        query = GDO_SpiderChannel.table().select()
        query.where(f"sc_spider_server={state.get_id()} AND sc_state='{GDO_SpiderChannel.UNVISITED}'")
        channel = query.order('RAND()').limit(1).exec().fetch_object()
        if not channel:
            return False
        return await Spider.visit_channel(state, channel)

    async def gdo_execute(self) -> GDT:
        if not await self.on_timer():
            return self.err('err_irc_spider_channels')
        active = GDO_SpiderServer.active()
        state = active[0]
        channel = GDO_SpiderChannel.table().get_by_vals({
            'sc_spider_server': state.get_id(),
            'sc_state': GDO_SpiderChannel.VISITING,
        })
        self.msg('msg_irc_spider_channel', (channel.gdo_val('sc_name'),))
        return self.empty()
