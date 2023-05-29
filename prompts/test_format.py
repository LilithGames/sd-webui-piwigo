import re
import unittest

from prompts.prompt import get_prompts

class TestPrompts(unittest.IsolatedAsyncioTestCase):

    def test_case1(self):
        s = '''
        masterpiece, ((best quality)), (1girl:1.5),, (white hair ), {blue eyes}, {{loot at viewer}}, [[ahoge]], <lora:xiaochun_v7:1>, [blue:red:0.4], [boy|girl|boy|girl|boy|girl], <hypernet:forest_5k:1.2>, (akishi \(fate\):1.5)
        girl, beautiful, (blonde:2), (long hair:1.5), (smiling face:1.3), (white skin:1.2), (blue eyes:1.1), in a field of (flowers:1.2) under the (sun:0.7)
        hello
        world
        '''
        print(get_prompts(s))
