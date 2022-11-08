import typing


async def unravel_hierarchical_fields(entry: typing.Dict[str, typing.Any],
                                field_name: str,
                                callback: typing.Callable[[typing.Dict[str, typing.Any], str],
                                                          typing.Awaitable[typing.Dict[str, typing.Any]]]) \
        -> typing.Any:
    field_split = field_name.split('.', 2)
    if field_split[0] in entry:
        if len(field_split) == 2:
            if isinstance(entry[field_split[0]], list):
                for i in range(len(entry[field_split[0]])):
                    entry[field_split[0]][i] = await unravel_hierarchical_fields(entry[field_split[0]][i],
                                                                                 field_split[1],
                                                                                 callback)
            else:
                entry[field_split[0]] = await unravel_hierarchical_fields(entry[field_split[0]],
                                                                          field_split[1],
                                                                          callback)
        else:
            entry = await callback(entry, field_split[0])
    return entry
