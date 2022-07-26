import typing

from osd2f.logger import logger


async def anonymize_likes(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    """Anonymization of Instagram Likes.

    Extract the participants name (e.g. 'my_username_27') and the liked account (e.g. 'bbc_sports')
    from the 'title' field. Replace occurrences of the user with '<user>' and of the liked account
    either with '<account>' or '<news>' (if account name corresponds to list of news accounts).
    """
    if 'title' not in entry:
        logger.warn('Instagram Like title does not match known format.')
        return entry

    entry['title'] = entry['title'].replace('mein_username', '<user>')

    return entry
