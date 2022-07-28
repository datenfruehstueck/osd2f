import typing

from osd2f.logger import logger


async def anonymize_likes(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    if 'following.userLink' not in entry:
        logger.warn('Instagram Like title does not match known format.')
        return entry

    entry['following.userLink'] = entry['following.userLink'].replace('twitter.com', 'haim.it')
    #if entry['title'] not in news:
    #    entry['title'] = '<user>'

    return entry
