import io
import os
import unittest
import asyncio
import aiofiles
import time
import threading
import re

from dotenv import load_dotenv
from piwigo.client import Piwigo

load_dotenv()
PIWIGO_HOST=os.environ["PIWIGO_HOST"]
PIWIGO_USER=os.environ["PIWIGO_USER"]
PIWIGO_PASS=os.environ["PIWIGO_PASS"]

async def my_coroutine(task_name, seconds_to_sleep=3):
    print(f'{task_name} has started! Will sleep for {seconds_to_sleep} seconds')
    await asyncio.sleep(seconds_to_sleep)
    print(f'{task_name} has finished!')

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def new_background_event_loop():
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=start_event_loop, args=(loop,))
    thread.start()
    return loop

loop = new_background_event_loop()

def extract_prompts(input_str):
    prompts = input_str.split(',')
    result = []
    for prompt in prompts:
        prompt = re.sub(r'[\[\]\{\}<>]', '', prompt).strip()  # 删除其他括号，只保留圆括号
        tokens = re.findall(r'[a-zA-Z0-9_:|. ()-]+', prompt)
        if ':' in prompt:
            # 如果提示词中有冒号，我们只保留冒号前的部分
            tokens = tokens[0].split(':')[:-1]
            word = ':'.join(tokens)
            if '(' in word and ')' in word:
                word = word.replace(':', '')
        elif '|' in prompt:
            word = '|'.join(tokens)
        else:
            word = ' '.join(tokens)
        if word:
            result.append(word.strip())
    return result


class TestPiwigoClient(unittest.IsolatedAsyncioTestCase):

    def test_piwigo_client(self):
        client = Piwigo(PIWIGO_HOST)
        print(client.pwg.getVersion())
        client.pwg.session.login(username=PIWIGO_USER, password=PIWIGO_PASS)
        img = client.pwg.images.addSimple(image="example/1.png", comment="hello", tags="tag1,tag2")
        print(img.get("image_id"))
        img_info = client.pwg.images.getInfo(image_id=img.get("image_id"))
        print(img_info.get("categories"))

    async def test_async_piwigo_client(self):
        client = Piwigo(PIWIGO_HOST)
        print(await client.pwg.getVersion.async_call())
        print(await client.pwg.session.login.async_call(username=PIWIGO_USER, password=PIWIGO_PASS))
        print(client._cookies)
        # p = await aiofiles.open("example/1.png", mode='rb')
        # data = await p.read()
        # img = await client.pwg.images.addSimple.async_call(image=data, comment="hello", tags="tag1,tag2")
        # print(img.get("image_id"))
        # await p.close()
        # await client.pwg.images.setInfo.async_call(image_id=img.get("image_id"), categories="1;")
        # img_info = await client.pwg.images.getInfo.async_call(image_id=img.get("image_id"))
        # print(img_info.get("categories"))

    def test_asyncio(self):
        asyncio.run_coroutine_threadsafe(my_coroutine('task1', 1), loop)
        asyncio.run_coroutine_threadsafe(my_coroutine('task2', 1), loop)
        time.sleep(10)

    def test_play(self):
        bs = io.BytesIO()
        print(type(bs.read()))

    def test_tags(self):
        s = 'masterpiece, ((best quality)), (1girl:1.5),, (white hair ), {blue eyes}, {{loot at viewer}}, [[ahoge]], <lora:xiaochun_v7:1>, [blue:red:0.4], [boy|girl|boy|girl|boy|girl], <hypernet:forest_5k:1.2>, (akishi \(fate]):1.5)'
        print(extract_prompts(s))
