import typing

from osd2f.logger import logger


def anonymize_generic(field: str, sep_strings: list) -> str:
    for sep_string in sep_strings:
        if sep_string[0] and sep_string[1] in field:
            names, rest = field.split(sep_string[0])
            rest_2 = rest.split(sep_string[1])[0]
            return field.replace(names, "<user> ").replace(rest_2, " <other> ")

    return field


async def fb_anonymize_comments(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    if "title" in entry:
        sep_strings = [
            # en
            ["commented", "on her own post."],
            ["commented", "on his own post."],
            ["replied", "to her own comment."],
            ["replied", "to his own comment."],
            ["commented on", "video."],
            ["commented on", "post."],
            # de
            ["hat auf", "Kommentar geantwortet."],
            ["hat", "Foto kommentiert."],
            ["hat", "Beitrag kommentiert."],
            ["hat", "seinen eigenen Beitrag kommentiert."],
            ["hat", "ihren eigenen Beitrag kommentiert."]
        ]
        entry["title"] = anonymize_generic(entry['title'], sep_strings)

    return entry


async def fb_anonymize_reactions(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    if "title" in entry:
        sep_strings = [
            # en
            ["likes", "her own post."],
            ["likes", "his own post."],
            ["liked", "this"],
            ["reacted to", "post."],
            ["likes", "post."],
            ["likes", "photo"],
            ["likes", "comment."],
            ["reacted to", "comment."],
            # de
            ["gefällt", "Beitrag."],
            ["gefällt", "Beitrag in Seite."],
            ["gefällt", "Kommentar."],
            ["gefällt", "Foto."],
            ["gefällt", "Video."],
            ["gefällt", "Beitrag in seiner eigenen Chronik."],
            ["gefällt", "Beitrag in ihrer eigenen Chronik."],
            ["hat", "auf einen Beitrag reagiert."]
        ]
        entry["title"] = anonymize_generic(entry['title'], sep_strings)

    return entry


async def fb_anonymize_usernames(entry: typing.Dict[str, typing.Any], _: str = '') -> typing.Dict[str, typing.Any]:
    if "name" in entry:
        list_nachrichten = ["Süddeutsche",
                            "BBC"]

        if entry['name'] not in list_nachrichten:
            entry['name'] = '<user>'

    return entry