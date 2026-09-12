import unittest

from gdo.irc_spider.module_irc_spider import module_irc_spider


class IRCSpiderModuleTest(unittest.TestCase):
    def test_requires_irc(self):
        self.assertEqual(['irc'], module_irc_spider().gdo_dependencies())
