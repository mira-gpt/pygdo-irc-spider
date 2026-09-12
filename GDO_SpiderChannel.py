from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Enum import GDT_Enum
from gdo.core.GDT_Object import GDT_Object
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.irc_spider.GDO_SpiderServer import GDO_SpiderServer


class GDO_SpiderChannel(GDO):
    UNVISITED = 'unvisited'
    VISITING = 'visiting'
    SUCCESS = 'success'
    FAILED = 'failed'
    EXPIRED = 'expired'

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('sc_id'),
            GDT_Object('sc_spider_server').table(GDO_SpiderServer.table()).not_null().cascade_delete(),
            GDT_String('sc_name').not_null().maxlen(96),
            GDT_UInt('sc_users').not_null().initial('0'),
            GDT_Enum('sc_state').choices({
                self.UNVISITED: self.UNVISITED,
                self.VISITING: self.VISITING,
                self.SUCCESS: self.SUCCESS,
                self.FAILED: self.FAILED,
                self.EXPIRED: self.EXPIRED,
            }).not_null().initial(self.UNVISITED),
            GDT_Timestamp('sc_last_visit'),
        ]

    @classmethod
    def for_channel(cls, spider_server: GDO_SpiderServer, name: str):
        state = cls.table().get_by_vals({
            'sc_spider_server': spider_server.get_id(),
            'sc_name': name,
        })
        return state or cls.blank({
            'sc_spider_server': spider_server.get_id(),
            'sc_name': name,
        }).insert()
