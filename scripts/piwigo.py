import io
import asyncio
import gradio as gr
import os
import logging
import threading
import time

import modules.scripts as scripts
from modules import shared
from modules import script_callbacks
from piwigo.client import Piwigo
from prompts.prompt import get_prompts

temp_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "temp"))

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def new_background_event_loop():
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=start_event_loop, args=(loop,))
    thread.start()
    return loop

background = new_background_event_loop()

def singleton(func):
    instance = None
    last_executed = 0
    async def wrapper(*args, **kwargs):
        nonlocal instance, last_executed
        current_time = time.time()
        if instance is None or current_time - last_executed >= 3600:
            instance = await func(*args, **kwargs)
            last_executed = current_time
        return instance

    return wrapper

@singleton
async def create_piwigo():
    client = Piwigo(shared.opts.piwigo_host)
    result = await client.pwg.session.login.async_call(username=shared.opts.piwigo_username, password=shared.opts.piwigo_password)
    if not result:
        logging.warning("piwigo login failed")
        return None
    return client

async def upload_images(processed):
    try:
        images = processed.images
        infotexts = processed.infotexts
        prompt = processed.prompt
        client = await create_piwigo()
        if not client:
            logging.warning("get piwigo client failed, skip upload")
            return
        extra = len(images) - len(infotexts)
        if extra > 0:
            # skip grid image
            images = images[extra:]
        for i in range(0, len(images)):
            image = images[i]
            infotext = infotexts[i]
            tags = get_prompts(prompt)
            desc = infotext
            with io.BytesIO() as output:
                image.save(output, 'PNG')
                data = output.getvalue()
                uploaded_image = await client.pwg.images.addSimple.async_call(image=data, comment=desc, tags=",".join(tags))
                image_id = uploaded_image.get("image_id")
                await client.pwg.images.setInfo.async_call(image_id=image_id, categories=shared.opts.piwigo_category_ids)
                print("uploaded: ", desc, tags)
    except Exception as e:
        logging.exception(f"An exception occurred while upload_images: {str(e)}, processd: {processed.images} {processed.infotexts} {processed.prompt}")


class PiwigoScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
            return "Piwigo"

        def show(self, is_img2img):
            return scripts.AlwaysVisible

        def ui(self, is_img2img):
            return []

        def postprocess(self, p, processed, *args):
            if shared.opts.piwigo_enable:
                asyncio.run_coroutine_threadsafe(upload_images(processed), background)
                print()


def on_ui_settings():
    section = ('piwigo', "Piwigo")
    shared.opts.add_option("piwigo_enable", shared.OptionInfo(False, "enable", gr.Checkbox, {}, section=section))
    shared.opts.add_option("piwigo_host", shared.OptionInfo("https://piwigohost.com", "base url", gr.Textbox, {}, section=section))
    shared.opts.add_option("piwigo_username", shared.OptionInfo("stable-diffusion", "username", gr.Textbox, {}, section=section))
    shared.opts.add_option("piwigo_password", shared.OptionInfo("", "password", gr.Textbox, {}, section=section))
    shared.opts.add_option("piwigo_category_ids", shared.OptionInfo("1;", "album ids", gr.Textbox, {}, section=section))

script_callbacks.on_ui_settings(on_ui_settings)
