import unittest
from unittest.mock import AsyncMock, Mock, patch

from gdo.base.Application import Application
from gdo.irc_spider.Spider import Spider
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel


class LifecycleTest(unittest.IsolatedAsyncioTestCase):
    async def test_expiry_only_selects_pending_visits(self):
        state, visit = Mock(), Mock()
        state.get_id.return_value = '3'
        connector = state.get_server().get_connector()
        connector.send_raw = AsyncMock()
        visit.gdo_value.return_value.timestamp.return_value = Application.TIME - 100
        visit.gdo_val.return_value = '#test'
        with patch('gdo.irc_spider.Spider.GDO_SpiderChannel.table') as table:
            table.return_value.all.return_value = [visit]
            await Spider.expire_visits(state, 101)
            visit.save_val.assert_not_called()
            await Spider.expire_visits(state, 100)
            self.assertIn("sc_state='%s'" % GDO_SpiderChannel.VISITING, table.return_value.all.call_args.args[0])
        visit.save_val.assert_called_once_with('sc_state', GDO_SpiderChannel.EXPIRED)
        connector.send_raw.assert_awaited_once()

    async def test_disabled_cleans_visits_without_requesting_lists(self):
        state = Mock()
        with patch.object(Spider, 'module') as module, patch('gdo.irc_spider.Spider.GDO_SpiderServer.table') as table, patch.object(Spider, 'expire_visits', new_callable=AsyncMock) as expire, patch.object(Spider, 'request_list', new_callable=AsyncMock) as listing:
            module.return_value.get_config_value.side_effect = lambda key: False if key == 'irc_spider_enabled' else 100
            table.return_value.all.return_value = [state]
            await Spider.on_timer()
            expire.assert_awaited_once_with(state, 0)
            listing.assert_not_awaited()

    async def test_reconnect_expires_old_pending_visits(self):
        server = Mock()
        with patch('gdo.irc_spider.Spider.GDO_SpiderServer.table') as table, patch.object(Spider, 'expire_visits', new_callable=AsyncMock) as expire:
            await Spider.on_reconnected(server, None)
            expire.assert_awaited_once_with(table.return_value.get_by_vals.return_value, 0)

    async def test_kick_marks_failed_and_disables_autojoin(self):
        server = Mock()
        with patch('gdo.irc_spider.Spider.GDO_SpiderServer.table'), patch('gdo.irc_spider.Spider.GDO_SpiderChannel.table') as table, patch('gdo.irc.method.join.join') as join:
            await Spider.on_bot_kicked(server, '#test', 'bye')
            table.return_value.get_by_vals.return_value.save_val.assert_called_once_with('sc_state', GDO_SpiderChannel.FAILED)
            join.return_value.env_server.return_value.env_channel.return_value.save_config_channel.assert_called_once_with('auto_join', '0')
