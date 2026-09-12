from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDO_Channel import GDO_Channel
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Object import GDT_Object
from gdo.date.GDT_Timestamp import GDT_Timestamp


class GDO_SpiderServer(GDO):
    """Persistent Spider state for one explicitly selected IRC server."""

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('ss_id'),
            GDT_Object('ss_server').table(GDO_Server.table()).not_null().unique().cascade_delete(),
            GDT_Object('ss_control_channel').table(GDO_Channel.table()).cascade_delete(),
            GDT_Bool('ss_active').not_null().initial('0'),
            GDT_Bool('ss_list_pending').not_null().initial('0'),
            GDT_Timestamp('ss_last_list'),
        ]

    @classmethod
    def for_server(cls, server: GDO_Server):
        state = cls.table().get_by_vals({'ss_server': server.get_id()})
        return state or cls.blank({'ss_server': server.get_id()}).insert()

    def get_server(self) -> GDO_Server:
        return self.gdo_value('ss_server')

    def get_control_channel(self) -> GDO_Channel | None:
        return self.gdo_value('ss_control_channel')

    @classmethod
    def active(cls) -> list['GDO_SpiderServer']:
        return cls.table().all('ss_active=1')
