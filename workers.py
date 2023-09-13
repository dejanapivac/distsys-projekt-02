import asyncio

from aiohttp import web

routes = web.RouteTableDef()


@routes.post("/startWorkers")
async def start_workers_endpoint(request):
    json_request = await request.json()
    ports = []
    for x in range(0, json_request):
        ports.append(8011 + x)
    asyncio.create_task(start_workers(ports))
    return web.json_response({"ports": ports}, status=200)


async def start_workers(ports):
    tasks = []
    for port in ports:
        worker = web.Application(client_max_size=20 * 1024 * 1024)
        worker.add_routes([web.post("/wordCounter", word_counter)])
        runner = web.AppRunner(worker)
        await runner.setup()
        tasks.append(web.TCPSite(runner, '127.0.0.1', port).start())
    await asyncio.gather(*tasks)


async def word_counter(request):
    json_request = await request.json()
    result = []
    for client_code in json_request:
        words = client_code["code"].replace('\n', ' ').split()
        words = len(words)
        result.append({"id": client_code["id"], "word_number": words})
    return web.json_response(result, status=200)

app = web.Application()
app.router.add_routes(routes)
web.run_app(app, port=8010)
