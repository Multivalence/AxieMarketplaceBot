from ext.errors import FilterNotFound

async def is_file_valid(ctx):

    if len(ctx.message.attachments) == 0:
        raise FilterNotFound

    url = ctx.message.attachments[0].url

    if not url.endswith('.json'):
        raise FilterNotFound

    return True