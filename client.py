import asyncio

import pandas as pd
import aiohttp


def client_extraction():
    df = pd.read_json('file-000000000040.json', lines=True, nrows=10000)
    content = [getattr(x, "content") for x in df.itertuples()]
    result = []
    for index, x in enumerate(content):
        result.append({"id": index, "code": x})
    return result


async def process():
    result = client_extraction()
    async with aiohttp.ClientSession() as session:
        response = await session.post("http://127.0.0.1:8080/processData", json=result)
        response = await response.json()
        for client_code in result:
            code = client_code['code']
            cleaned_code = code.replace('\n', ' ').strip().split()
            letter_count = sum(len(word) for word in cleaned_code)
            word_count = [client_word_count['word_number'] for client_word_count in response if
                          client_word_count['id'] == client_code['id']]
            avg_length = letter_count / word_count[0]
            print("Client: ", client_code['id'], ", average letter count: ", avg_length)


asyncio.run(process())
