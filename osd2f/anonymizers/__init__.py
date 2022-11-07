"""Anonymizers

This sub-module contains functions that operate on individual entries
to do some form of anonymization, either by redacting (parts of) strings,
or by omitting entries entirely (e.g. returning None for some entries).

All anonymization functions should have the (entry, optional_string_param)
signature.

Anonymization here generally means to replace username/pages with a generic "<user>", unless the username is known
as a media outlet's user. Lists of respective usernames are hard-coded here for the German-speaking context.

Register:
- fb_anonymize_reactions: anonymizes "x likes y's post"-like strings
- fb_anonymize_comments: anonymizes "x commented on its own post"-like strings
- fb_anonymize_usernames: anonymizes simple usernames (e.g., in following lists)
- insta_anonymize_text: anonymizes mentioned users in a text (with multiple occurrences also)
- insta_anonymize_usernames: anonymizes simple usernames (e.g., in following lists)
- insta_anonymize_following: anonymizes follow lists which contain URLs to user profiles
- twitter_anonymize_handles: anonymizes mentioned users in a text (with multiple occurrences also)
- twitter_anonymize_usernames: anonymizes simple usernames (without @)
- youtube_extract_timestamp: extracts UTC timestamp from string
"""

import re
import typing

from .facebook import fb_anonymize_reactions, fb_anonymize_comments, fb_anonymize_usernames
from .instagram import insta_anonymize_text, insta_anonymize_usernames, insta_anonymize_following
from .twitter import twitter_anonymize_handles
from .youtube import youtube_extract_timestamp
from ..definitions import Submission, SubmissionList, UploadSettings
from ..logger import logger

options: typing.Dict[str, typing.Callable[[typing.Dict, str], typing.Awaitable]] = {
    'fb_anonymize_reactions': fb_anonymize_reactions,  # noqa
    'fb_anonymize_comments': fb_anonymize_comments,  # noqa
    'insta_anonymize_text': insta_anonymize_text,  # noqa
    'fb_anonymize_usernames': fb_anonymize_usernames,  # noqa
    'insta_anonymize_usernames': insta_anonymize_usernames,  # noqa
    'insta_anonymize_following': insta_anonymize_following,  # noqa
    'twitter_anonymize_handles': twitter_anonymize_handles,  # noqa
    'youtube_extract_timestamp': youtube_extract_timestamp  # noqa
}


async def apply(
    file_entries: typing.List[typing.Dict[str, typing.Any]],
    anonymizer: str,
    optional_str_param: str = "",
) -> typing.List[typing.Dict[str, typing.Any]]:
    if anonymizer not in options:
        logger.warning(
            f"Specified anonymizer {anonymizer} not found. "
            f"Available anonymizers: {options}."
        )
        return []

    anonymized_entries = []
    for entry in file_entries:
        if entry is None:
            continue
        try:
            processed_entry = await options[anonymizer](entry, optional_str_param)
            anonymized_entries.append(processed_entry)
        except:  # noqa
            logger.warning(
                f"anonymizer `{anonymizer}` threw an error while parsing an entry"
            )
            continue

    return anonymized_entries


async def anonymize_submission(submission: Submission, settings: UploadSettings):
    for filename_pattern, setting in settings.files.items():
        logger.debug(f"matching {filename_pattern} to {submission.filename}")
        if not re.search(filename_pattern, submission.filename):
            continue
        # disregards settings for which no anonymizers are registered
        if not setting.anonymizers:
            continue
        logger.debug(f"Applying {setting.anonymizers} to {submission.filename}")
        # apply all anonymizers registered for file pattern
        for anonymizer in setting.anonymizers:
            function_name, arg = anonymizer.copy().popitem()
            logger.debug(f"Applying {function_name} to {submission.filename}")

            submission.entries = await apply(
                file_entries=submission.entries,
                anonymizer=function_name,
                optional_str_param=arg,
            )
        # only match the first matching setting
        break
    return submission


async def anonymize_submission_list(
    submission_list: SubmissionList, settings: UploadSettings
) -> SubmissionList:
    for i, submission in enumerate(submission_list.__root__):
        logger.debug(f"at submission {i}")
        await anonymize_submission(submission, settings)
    return submission_list
