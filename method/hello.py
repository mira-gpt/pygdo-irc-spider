from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.irc.method.join import join
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer


class hello(Method):
    @classmethod
    def gdo_trigger(cls) -> str:
        return 'hello'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_in_private(self) -> bool:
        return False

    async def gdo_execute(self) -> GDT:
        channel = self._env_channel
        if not channel:
            return self.err('err_irc_spider_channel')
        state = GDO_SpiderServer.table().get_by_vals({'ss_server': channel.get_server().get_id()})
        if not state:
            return self.err('err_irc_spider_channel')
        visit = GDO_SpiderChannel.table().get_by_vals({
            'sc_spider_server': state.get_id(),
            'sc_name': channel.get_name(),
            'sc_state': GDO_SpiderChannel.VISITING,
        })
        if not visit:
            return self.err('err_irc_spider_channel')
        join().env_copy(self).save_config_channel('auto_join', '1')
        visit.save_val('sc_state', GDO_SpiderChannel.SUCCESS)
        self.msg('msg_irc_spider_hello')
        return self.empty()
