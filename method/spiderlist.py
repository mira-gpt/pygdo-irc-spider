from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer
from gdo.irc_spider.Spider import Spider


class spiderlist(Method):
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'spider.list'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return []

    async def gdo_execute(self) -> GDT:
        active = GDO_SpiderServer.active()
        if not active:
            return self.err('err_irc_spider_server')
        state = active[0]
        if self._env_channel:
            state.save_val('ss_control_channel', self._env_channel.get_id())
        if await Spider.request_list(state):
            self.msg('msg_irc_spider_list')
        else:
            return self.err('err_irc_spider_connected')
        return self.empty()
