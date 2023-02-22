from config import (VKAPP_TOKEN,
                    TGBOT_TOKEN,
                    TG_API_ID,
                    TG_API_HASH,
                    VK_GROUP_ID,
                    VK_API_VERSION,
                    TG_CHANNEL_NAME)
from pyrogram import Client
import asyncio
import aiohttp
import aiofiles
import templates


vk_api_wall_get = 'https://api.vk.com/method/wall.get'

vk_params = {'access_token': VKAPP_TOKEN,
             'v': VK_API_VERSION,
             'owner_id': VK_GROUP_ID,
             'count': 25}


class VKPost:
    def __init__(self, post_object: dict) -> None:
        self.post_object = post_object

        post_owner_id = self.post_object['owner_id']
        post_id = self.post_object['id']
        self.post_link = f'vk.com/wall{post_owner_id}_{post_id}'
        
        self.post_text = self.post_object.get('text', '')
    
    def __get_photo_max_size(self, photo: dict) -> str:
        max_height = 0
        max_width = 0
        best_size = {}

        for size in photo['sizes']:
            current_height = size['height']
            current_width = size['width']

            if (current_height > max_height) and (current_width > max_width):
                max_height = current_height
                max_width = current_width
                best_size = size
            
        return best_size['url']
    
    def extract_attachments(self) -> dict:
        attachments = {'photos': [],
                       'videos': [],
                       'docs': [],
                       'poll': {},
                       'link': {},
                       'product': {}}

        for attachment in self.post_object['attachments']:
            match attachment['type']:
                case 'photo':
                    photo_url = self.__get_photo_max_size(attachment['photo'])
                    attachments['photos'].append(photo_url)
                case 'video':
                    video_owner_id = attachment['video']['owner_id']
                    video_id = attachment['video']['id']
                    attachments['videos'].append(f'vk.com/video{video_owner_id}_{video_id}')
                case 'doc':
                    attachments['docs'].append(attachment['doc']['url'])
                case 'poll':
                    poll_question = attachment['poll']['question']
                    is_anonymous = attachment['poll']['anonymous']
                    poll_answers = [answer['text'] for answer in attachment['poll']['answers']]
                    
                    attachments['poll'] = {'poll_question': poll_question,
                                           'is_anonymous': is_anonymous,
                                           'answers': poll_answers}
                case 'market':
                    product_description = attachment['market']['description']
                    product_title = attachment['market']['title']
                    product_photo_url = attachment['market']['thumb_photo']
                    product_SKU = attachment['market']['sku']
                    product_price = attachment['market']['price']['text']
                    
                    product_owner_id = attachment['market']['owner_id']
                    product_id = attachment['market']['id']
                    product_url = f'vk.com/product{product_owner_id}_{product_id}'
                    
                    attachments['product'] = {'description': product_description,
                                              'title': product_title,
                                              'photo_url': product_photo_url,
                                              'SKU': product_SKU,
                                              'price': product_price,
                                              'product_url': product_url}
                case 'link':
                    match attachment['link']['description']:
                        case 'Playlist':
                            attachments['link'] = {'type': 'Playlist',
                                                   'title': attachment['link']['title'],
                                                   'url': attachment['link']['url'].replace('m.', '')}
                        case 'Article':
                            article_photo_url = self.__get_photo_max_size(attachment['link']['photo'])
                            attachments['link'] = {'type': 'Article',
                                                   'title': attachment['link']['title'],
                                                   'url': attachment['link']['url'].replace('m.', ''),
                                                   'photo_url': article_photo_url}
        return attachments


async def get_vk_last_posts() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(vk_api_wall_get, params=vk_params) as response:
            return await response.json()


async def main(delay=5):
    app = Client(name='priscilla_eF_bot',
             api_id=TG_API_ID,
             api_hash=TG_API_HASH,
             bot_token=TGBOT_TOKEN)

    while True:
        vk_posts = await get_vk_last_posts()

        for post in vk_posts['response']['items']:
            vk_post = VKPost(post)

            async with aiofiles.open('posted.txt', 'a+') as file:
                await file.seek(0)
                posted = await file.read()
                if vk_post.post_link in posted:
                    print(f'{vk_post.post_link} already in Telegram')
                    continue
                else:
                    await file.write(vk_post.post_link + '\n')
            
            attachments = vk_post.extract_attachments()
            #if not all(attachments.values()):
            #    async with app:
            #        await app.send_message(TG_CHANNEL_NAME, vk_post.post_text)
            #    continue
            
            for attachment in attachments:
                if attachments[attachment]:
                    match attachment:
                        case 'poll':
                            async with app:
                                if vk_post.post_text:
                                    await app.send_message(TG_CHANNEL_NAME, vk_post.post_text)
                                await app.send_poll(TG_CHANNEL_NAME,
                                                    question=attachments['poll']['poll_question'],
                                                    options=attachments['poll']['answers'],
                                                    is_anonymous=attachments['poll']['is_anonymous'])
                        case 'product':
                            async with app:
                                if vk_post.post_text:
                                    await app.send_message(TG_CHANNEL_NAME, vk_post.post_text)
                                await app.send_photo(TG_CHANNEL_NAME,
                                                     photo=attachments['product']['photo_url'],
                                                     caption=templates.product_message.format(**attachments['product']))

        await asyncio.sleep(delay)
        break


if __name__ == '__main__':
    asyncio.run(main())
