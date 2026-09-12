import unittest
from unittest.mock import AsyncMock, Mock, patch

from gdo.base.Application import Application
from gdo.base.Events import Events
from gdo.base.Render import Mode
from gdo.irc.method.CMD_322 import CMD_322
from gdo.irc.method.CMD_323 import CMD_323
from gdo.irc.method.CMD_KICK import CMD_KICK


class IRCListEventTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Application.EVENTS = Events()
        Application.mode(Mode.render_irc)

    async def test_list_entry_is_published(self):
        command = CMD_322()
        command._env_server = Mock()
        command._irc_params = ['Mira', '#example', '42', 'Example topic']
        with patch('gdo.irc.method.CMD_322.Application.EVENTS.publish', new=AsyncMock()) as publish:
            await command.gdo_execute()
        publish.assert_awaited_once_with('irc_list_entry', command._env_server, '#example', 42, 'Example topic')

    async def test_list_end_is_published(self):
        command = CMD_323()
        command._env_server = Mock()
        with patch('gdo.irc.method.CMD_323.Application.EVENTS.publish', new=AsyncMock()) as publish:
            await command.gdo_execute()
        publish.assert_awaited_once_with('irc_list_finished', command._env_server)

    async def test_own_kick_is_published(self):
        connector = Mock()
        connector._own_nick = 'Mira'
        command = CMD_KICK()
        command._env_server = Mock()
        command._irc_params = ['#example', 'mIrA', 'No bots']
        command.irc_connector = Mock(return_value=connector)
        with patch('gdo.irc.method.CMD_KICK.Application.EVENTS.publish', new=AsyncMock()) as publish:
            await command.gdo_execute()
        publish.assert_awaited_once_with('irc_bot_kicked', command._env_server, '#example', 'No bots')
