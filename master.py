import random

import aiohttp
from aiohttp import web

routes = web.RouteTableDef()


async def start_workers(session):
    number_of_workers = random.randint(5, 10)
    response = await session.post("http://127.0.0.1:8010/startWorkers", json=number_of_workers)
    ports = await response.json()
    workers = []
    for port in ports:
        workers.append({'wokrer_id': port, 'client_ids': []})
    return workers


@routes.post("/processData")
async def get_data(request):
    try:
        json_request = await request.json()
        async with aiohttp.ClientSession() as session:
            await start_workers(session)

        return web.json_response(status=200)
    except Exception as e:
        print(e)
        return web.json_response({"status": "failed"}, status=500)


app = web.Application(client_max_size=20 * 1024 * 1024)
app.router.add_routes(routes)
web.run_app(app, port=8080)
