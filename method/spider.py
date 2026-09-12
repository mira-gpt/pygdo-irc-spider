from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDO_Permission import GDO_Permission
from gdo.irc_spider.module_irc_spider import module_irc_spider
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel


class spider(Method):
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'spider'

    def gdo_user_permission(self) -> str | None:
        return GDO_Permission.STAFF

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Bool('enabled').positional()]

    async def gdo_execute(self) -> GDT:
        enabled = self.param_val('enabled')
        if enabled is None:
            module = module_irc_spider.instance()
            self.msg('msg_irc_spider_enabled' if module.get_config_value('irc_spider_enabled') else 'msg_irc_spider_disabled')
            states = GDO_SpiderServer.active()
            if not states:
                self.msg('msg_irc_spider_no_server')
            for state in states:
                counts = tuple(GDO_SpiderChannel.table().count_where(
                    f"sc_spider_server={state.get_id()} AND sc_state='{status}'"
                ) for status in (GDO_SpiderChannel.UNVISITED, GDO_SpiderChannel.VISITING,
                                 GDO_SpiderChannel.SUCCESS, GDO_SpiderChannel.FAILED,
                                 GDO_SpiderChannel.EXPIRED))
                self.msg('msg_irc_spider_stats', (state.get_server().get_name(), *counts))
            return self.empty()
        await module_irc_spider.instance().save_config_val('irc_spider_enabled', enabled)
        self.msg('msg_irc_spider_enabled' if enabled == '1' else 'msg_irc_spider_disabled')
        return self.empty()
