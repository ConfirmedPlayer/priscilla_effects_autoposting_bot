from config import VKAPP_TOKEN, TGBOT_TOKEN, VK_GROUP_ID, VK_API_VERSION
import asyncio
import aiohttp


vk_api_wall_get = 'https://api.vk.com/method/wall.get'

tg_api_wall_get = f'https://api.telegram.org/bot{TGBOT_TOKEN}/getUpdates'

vk_params = {'access_token': VKAPP_TOKEN,
             'v': VK_API_VERSION,
             'owner_id': VK_GROUP_ID,
             'count': 25}

tg_params = {'allowed_updates': ['channel_post']}


class VKPost:
    def __init__(self, post_object: dict) -> None:
        self.post_object = post_object
    
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
    
    def extract_attachments(self):
        attachments = {'photos': [],
                       'videos': [],
                       'audios': [],
                       'docs': [],
                       'poll': {},
                       'link': {}}

        for attachment in self.post_object['attachments']:
            match attachment['type']:
                case 'photo':
                    photo_url = self.__get_photo_max_size(attachment['photo'])
                    attachments['photos'].append(photo_url)
                case 'video':
                    video_owner_id = attachment['video']['owner_id']
                    video_id = attachment['video']['id']
                    attachments['videos'].append(f'vk.com/video{video_owner_id}_{video_id}')
                case 'audio':
                    ...
                case 'doc':
                    attachments['docs'].append(attachment['doc']['url'])
                case 'poll':
                    poll_question = attachment['poll']['question']
                    is_anonymous = True if attachment['poll']['anonymous'] == 'true' else False
                    poll_answers = [answer['text'] for answer in attachment['poll']['answers']]
                    
                    attachments['poll'] = {'poll_question': poll_question,
                                           'is_anonymous': is_anonymous,
                                           'answers': poll_answers}
                case 'link':
                    match attachment['link']['description']:
                        case 'Playlist':
                            attachments['link'] = {'type': 'Playlist',
                                                   'title': attachment['link']['title'],
                                                   'url': attachment['link']['url']}
                        case 'Article':
                            article_photo_url = self.__get_photo_max_size(attachment['link']['photo'])
                            attachments['link'] = {'type': 'Article',
                                                   'title': attachment['link']['title'],
                                                   'url': attachment['link']['url'],
                                                   'photo_url': article_photo_url}
        return attachments
    
    def convert_to_telegram_post(self):
        text = self.post_object.get('text', '')


async def get_vk_last_posts() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(vk_api_wall_get, params=vk_params) as response:
            return await response.json()


async def get_tg_last_posts() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(tg_api_wall_get, params=tg_params) as response:
            return await response.text()


async def main(delay=5):
    while True:
        vk_posts = await get_vk_last_posts()

        for post in vk_posts['response']['items']:
            vk_post = VKPost(post).extract_attachments()
            print(vk_post)

        break#await asyncio.sleep(delay)


if __name__ == '__main__':
    asyncio.run(main())
