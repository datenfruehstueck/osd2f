import typing

from osd2f.logger import logger


async def anonymize_likes(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    if 'title' not in entry:
        logger.warn('Instagram Like title does not match known format.')
        return entry

    entry['title'] = entry['title'].replace('russellrodney', '<user>')
    #if entry['title'] not in news:
    #    entry['title'] = '<user>'

    return entry
