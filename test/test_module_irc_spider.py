import unittest
from unittest.mock import AsyncMock, Mock, patch

from gdo.base.Application import Application
from gdo.base.Events import Events
from gdo.base.Render import Mode
from gdo.irc_spider.module_irc_spider import module_irc_spider
from gdo.irc_spider.method.hello import hello
from gdo.irc_spider.method.spider import spider
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel


class IRCSpiderModuleTest(unittest.IsolatedAsyncioTestCase):
    async def test_status_does_not_change_enabled_setting(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        method = spider()
        method.param_val = Mock(return_value=None)
        method.msg = Mock()
        method.empty = Mock()
        with (
            patch('gdo.irc_spider.method.spider.module_irc_spider.instance') as module,
            patch('gdo.irc_spider.method.spider.GDO_SpiderServer.active', return_value=[]),
        ):
            module.return_value.get_config_value.return_value = False
            await method.gdo_execute()
            module.return_value.save_config_val.assert_not_called()
            method.msg.assert_any_call('msg_irc_spider_disabled')
            method.msg.assert_any_call('msg_irc_spider_no_server')

    async def test_explicit_zero_and_one_update_setting(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        for enabled in ('0', '1'):
            method = spider()
            method.param_val = Mock(return_value=enabled)
            method.msg = Mock()
            method.empty = Mock()
            with patch('gdo.irc_spider.method.spider.module_irc_spider.instance') as module:
                module.return_value.save_config_val = AsyncMock()
                await method.gdo_execute()
                module.return_value.save_config_val.assert_awaited_once_with('irc_spider_enabled', enabled)

    async def test_hello_persists_approval_and_enables_autojoin(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        method = hello()
        method._env_channel = Mock()
        method._env_channel.get_trigger.return_value = '.'
        method.msg = Mock()
        method.empty = Mock()
        with (
            patch('gdo.irc_spider.method.hello.GDO_SpiderServer.table') as servers,
            patch('gdo.irc_spider.method.hello.GDO_SpiderChannel.table') as channels,
            patch('gdo.irc_spider.method.hello.join') as autojoin,
        ):
            visit = channels.return_value.get_by_vals.return_value
            await method.gdo_execute()
            visit.save_val.assert_called_once_with('sc_state', GDO_SpiderChannel.SUCCESS)
            method.msg.assert_called_once_with('msg_irc_spider_hello')
            autojoin.return_value.env_copy.return_value.save_config_channel.assert_called_once_with('auto_join', '1')
            self.assertEqual(GDO_SpiderChannel.VISITING, channels.return_value.get_by_vals.call_args.args[0]['sc_state'])

    async def test_hello_rejects_channels_without_a_visit(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        method = hello()
        method._env_channel = Mock()
        method.err = Mock()
        with (
            patch('gdo.irc_spider.method.hello.GDO_SpiderServer.table'),
            patch('gdo.irc_spider.method.hello.GDO_SpiderChannel.table') as channels,
            patch('gdo.irc_spider.method.hello.join') as autojoin,
        ):
            channels.return_value.get_by_vals.return_value = None
            await method.gdo_execute()
            method.err.assert_called_once_with('err_irc_spider_channel')
            autojoin.assert_not_called()

    def test_requires_only_irc(self):
        self.assertEqual(['irc'], module_irc_spider().gdo_dependencies())

    def test_server_selection_requires_explicit_argument(self):
        from gdo.irc_spider.method.spiderserv import spiderserv
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        with patch('gdo.ui.WithIcon.t', return_value='numeric'), patch('gdo.core.GDO_Server.GDO_Server.table'):
            parameter = spiderserv().gdo_parameters()[0]
        self.assertTrue(parameter.is_not_null())
        self.assertFalse(parameter._default_current)
        self.assertIsNone(parameter.get_value())

    async def test_timer_triggers_spider_channel_when_enabled(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)
        module = module_irc_spider()
        module.get_config_value = lambda _key: True
        with (
            patch('gdo.irc_spider.module_irc_spider.Spider.on_timer', new=AsyncMock()) as spider_timer,
            patch('gdo.irc_spider.method.spider_channel.spider_channel.on_timer', new=AsyncMock()) as channel_timer,
        ):
            await module.on_timer()
        spider_timer.assert_awaited_once()
        channel_timer.assert_awaited_once()
