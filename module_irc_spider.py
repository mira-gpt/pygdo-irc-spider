from gdo.base.GDO_Module import GDO_Module


class module_irc_spider(GDO_Module):
    """Optional, inert boundary for future consent-aware IRC discovery."""

    def gdo_dependencies(self):
        return ['irc']
