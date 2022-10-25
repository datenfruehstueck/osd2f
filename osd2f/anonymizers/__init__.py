"""Anonymizers

This sub-module contains functions that operate on individual entries
to do some form of anonymization, either by redacting (parts of) strings,
or by omitting entries entirely (e.g. returning None for some entries).

All anonymization functions should have the (entry, optional_string_param)
signature.

Register

"""

import re
import typing

from .sample_platform import redact_text
from .facebook import fb_anonymize_reactions, fb_anonymize_comments, fb_anonymize_usernames, fb_anonymize_userdatanames, fb_anonymize_usertitles
from .instagram import insta_anonymize_comments, insta_anonymize_usernames, insta_anonymize_following, insta_anonymize_value, insta_anonymize_likes
from .twitter import twitter_anonymize_tweets, twitter_anonymize_likes
from ..definitions import Submission, SubmissionList, UploadSettings
from ..logger import logger

options: typing.Dict[str, typing.Callable[[typing.Dict, str], typing.Awaitable]] = {
    'redact_text': redact_text,  # noqa
    'fb_anonymize_reactions': fb_anonymize_reactions,  # noqa
    'fb_anonymize_comments': fb_anonymize_comments,  # noqa
    'fb_anonymize_usernames': fb_anonymize_usernames,  # noqa
    'fb_anonymize_userdatanames': fb_anonymize_userdatanames,  # noqa
    'fb_anonymize_usertitles': fb_anonymize_usertitles,  # noqa
    'insta_anonymize_comments': insta_anonymize_comments,  # noqa
    'insta_anonymize_usernames': insta_anonymize_usernames,  # noqa
    'insta_anonymize_following': insta_anonymize_following,  # noqa
    'insta_anonymize_value': insta_anonymize_value,  # noqa
    'insta_anonymize_likes': insta_anonymize_likes,  # noqa
    'twitter_anonymize_likes': twitter_anonymize_likes,  # noqa
    'twitter_anonymize_tweets': twitter_anonymize_tweets  # noqa
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
