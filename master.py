import asyncio
import random

import aiohttp
from aiohttp import web

routes = web.RouteTableDef()


async def start_workers(session):
    number_of_workers = random.randint(5, 10)
    response = await session.post("http://127.0.0.1:8010/startWorkers", json=number_of_workers)
    ports = await response.json()
    ports = ports['ports']
    workers = []
    for port in ports:
        workers.append({'port': port, 'client_ids': []})
    return workers


@routes.post("/processData")
async def get_data(request):
    try:
        json_request = await request.json()
        async with aiohttp.ClientSession() as session:
            tasks = []
            workers = await start_workers(session)
            for worker, client_code in exhausted_zip(chunk_list(json_request), workers):
                tasks.append(session.post(f"http://127.0.0.1:{worker['port']}/wordCounter", json=client_code))
            results = await asyncio.gather(*tasks)
            results = [await result.json() for result in results]
            print(results)
        return web.json_response(results, status=200)
    except Exception as e:
        print(e)
        return web.json_response({"status": "failed"}, status=500)


def chunk_list(lst):
    chunk = []
    result = []
    for i in lst:
        chunk.append(i)
        if len(chunk) >= 1000:
            result.append(chunk)
            chunk = []
    if chunk:
        result.append(chunk)
    return result


def exhausted_zip(list1, list2):
    result = []
    for i, item in enumerate(list1):
        other_index = i % len(list2)
        result.append((list2[other_index], item))
    return result


app = web.Application(client_max_size=20 * 1024 * 1024)
app.router.add_routes(routes)
web.run_app(app, port=8080)
