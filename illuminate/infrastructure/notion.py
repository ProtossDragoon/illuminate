import os

import dotenv
from notion_client import APIResponseError, Client

dotenv.load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError('Notion token not found.')

notion = Client(auth=NOTION_TOKEN)
database_id = 'ad5c0e93ae914b22b7d4c4148e8f6bfb'


def get_povs() -> list:
    try:
        response = notion.databases.query(
            database_id=database_id,
            page_size=100,
        )
    except APIResponseError as e:
        raise e from e

    def parse_pages(pages):
        page_titles = []
        for page in pages:
            for _, property in page['properties'].items():
                # NOTE: notion은 페이지 제목이 id가 title인 property라고 여김.
                if property['id'] == 'title':
                    page_titles.append(property['title'][0]['plain_text'])
        return page_titles

    return parse_pages(response['results'])


if __name__ == '__main__':
    from pprint import pprint

    from illuminate.log_utils import setup_logging

    setup_logging()
    pprint(get_povs())
