import asyncio

import pandas as pd
import aiohttp


def client_extraction():
    df = pd.read_json('file-000000000040.json', lines=True, nrows=1001)
    content = [getattr(x, "content") for x in df.itertuples()]
    result = []
    for index, x in enumerate(content):
        result.append({"id": index, "code": x})
    return result


async def process():
    result = client_extraction()
    async with aiohttp.ClientSession() as session:
        response = await session.post("http://127.0.0.1:8080/processData", json=result)
        print(response)


asyncio.run(process())
