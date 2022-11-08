import typing
import re
from .genuine import unravel_hierarchical_fields


async def youtube_extract_timestamp(entry: typing.Dict[str, typing.Any], text_field: str = '') \
        -> typing.Dict[str, typing.Any]:
    if text_field in entry:
        text_match = re.search('[12][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9] [012][0-9]:[0-5][0-9]:[0-5][0-9] UTC',
                               entry[text_field])
        if text_match:
            entry[text_field] = text_match.group(0)
    elif text_field.__contains__('.'):
        entry = await unravel_hierarchical_fields(entry, text_field, youtube_extract_timestamp)
    return entry
