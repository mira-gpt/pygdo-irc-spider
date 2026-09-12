from gdo.base.Application import Application
from gdo.date.Time import Time
from gdo.irc_spider.GDO_SpiderChannel import GDO_SpiderChannel
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer


class Spider:
    """State machine for LIST, one invitation, and explicit channel approval."""

    INTRODUCTION = (
        'Hello — I am Mira, a transparent discovery bot. '
        'Reply {trigger}hello to keep me here; otherwise I will leave in {timeout}.'
    )

    @classmethod
    def module(cls):
        from gdo.irc_spider.module_irc_spider import module_irc_spider
        return module_irc_spider.instance()

    @classmethod
    async def request_list(cls, state: GDO_SpiderServer):
        server = state.get_server()
        if server.get_connector_name() != 'irc' or not server.get_connector().is_connected():
            return False
        await server.get_connector().send_raw('LIST')
        state.save_val('ss_list_pending', '1')
        state.save_val('ss_last_list', Time.get_date())
        return True

    @classmethod
    async def on_timer(cls):
        module = cls.module()
        if not module.get_config_value('irc_spider_enabled'):
            return
        cooldown = module.get_config_value('irc_spider_cooldown')
        timeout = module.get_config_value('irc_spider_intro_timeout')
        for state in GDO_SpiderServer.active():
            await cls.expire_visits(state, timeout)
            last_list = state.gdo_value('ss_last_list')
            due = not last_list or Application.TIME - last_list.timestamp() >= cooldown
            # A server can lose its LIST end reply. The cooldown doubles as a
            # timeout for that stale request, so the spider can recover.
            if due:
                await cls.request_list(state)

    @classmethod
    async def expire_visits(cls, state: GDO_SpiderServer, timeout: float):
        where = f"sc_spider_server={state.get_id()} AND sc_state='{GDO_SpiderChannel.VISITING}'"
        for channel in GDO_SpiderChannel.table().all(where):
            last_visit = channel.gdo_value('sc_last_visit')
            if last_visit and Application.TIME - last_visit.timestamp() >= timeout:
                await state.get_server().get_connector().send_raw(f"PART {channel.gdo_val('sc_name')} :No approval received")
                channel.save_val('sc_state', GDO_SpiderChannel.EXPIRED)

    @classmethod
    async def on_list_entry(cls, server, name: str, users: int, _topic: str):
        state = GDO_SpiderServer.table().get_by_vals({'ss_server': server.get_id()})
        if not state or state.gdo_val('ss_active') != '1' or not name.startswith('#'):
            return
        channel = GDO_SpiderChannel.for_channel(state, name)
        if channel.gdo_val('sc_state') == GDO_SpiderChannel.UNVISITED:
            channel.save_val('sc_users', str(users))

    @classmethod
    async def on_list_finished(cls, server):
        state = GDO_SpiderServer.table().get_by_vals({'ss_server': server.get_id()})
        if not state:
            return
        state.save_val('ss_list_pending', '0')
        if channel := state.get_control_channel():
            await channel.send_text('msg_irc_spider_list_loaded', ())

    @classmethod
    async def visit_next(cls, state: GDO_SpiderServer):
        query = GDO_SpiderChannel.table().select()
        query.where(f"sc_spider_server={state.get_id()} AND sc_state='{GDO_SpiderChannel.UNVISITED}'")
        channel = query.order('RAND()').limit(1).exec().fetch_object()
        return await cls.visit_channel(state, channel)

    @classmethod
    async def visit_channel(cls, state: GDO_SpiderServer, channel: GDO_SpiderChannel | None):
        if not channel:
            return False
        if not state.get_server().get_connector().is_connected():
            return False
        visiting = GDO_SpiderChannel.table().get_by_vals({
            'sc_spider_server': state.get_id(),
            'sc_state': GDO_SpiderChannel.VISITING,
        })
        if visiting:
            return False
        channel.save_val('sc_state', GDO_SpiderChannel.VISITING)
        channel.save_val('sc_last_visit', Time.get_date())
        await state.get_server().get_connector().send_raw(f"JOIN {channel.gdo_val('sc_name')}")
        return True

    @classmethod
    async def on_bot_joined(cls, _user, channel):
        state = GDO_SpiderServer.table().get_by_vals({'ss_server': channel.get_server().get_id()})
        if not state:
            return
        visit = GDO_SpiderChannel.table().get_by_vals({
            'sc_spider_server': state.get_id(),
            'sc_name': channel.get_name(),
            'sc_state': GDO_SpiderChannel.VISITING,
        })
        if visit:
            from gdo.irc.method.join import join
            join().env_server(channel.get_server()).env_channel(channel).save_config_channel('auto_join', '0')
            timeout = cls.module().get_config_value('irc_spider_intro_timeout')
            visit.save_val('sc_last_visit', Time.get_date())
            await channel.send(cls.INTRODUCTION.format(
                trigger=channel.get_server().get_trigger(),
                timeout=Time.human_duration_en(timeout, n_units=6),
            ))

    @classmethod
    async def on_bot_kicked(cls, server, name: str, _reason: str):
        state = GDO_SpiderServer.table().get_by_vals({'ss_server': server.get_id()})
        if state and (visit := GDO_SpiderChannel.table().get_by_vals({
            'sc_spider_server': state.get_id(), 'sc_name': name,
        })):
            visit.save_val('sc_state', GDO_SpiderChannel.FAILED)
            if channel := server.get_channel_by_name(name):
                from gdo.irc.method.join import join
                join().env_server(server).env_channel(channel).save_config_channel('auto_join', '0')
