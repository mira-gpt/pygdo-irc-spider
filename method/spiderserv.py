from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_Permission import GDO_Permission
from gdo.core.GDT_Server import GDT_Server
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer


class spiderserv(Method):
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'spider.server'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Server('server').not_null().positional()]

    async def gdo_execute(self) -> GDT:
        server = self.param_value('server')
        if not server or server.get_connector_name() != 'irc':
            return self.err('err_irc_spider_server')
        for state in GDO_SpiderServer.active():
            state.save_val('ss_active', '0')
        state = GDO_SpiderServer.for_server(server)
        state.save_val('ss_active', '1')
        self.msg('msg_irc_spider_server', (server.get_name(),))
        return self.empty()
