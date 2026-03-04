import asyncio
import websockets
import json
import uuid

clients = {}
operator = None


async def handler(ws):

    global operator

    first = await ws.recv()
    data = json.loads(first)

    role = data["role"]

    if role == "operator":

        operator = ws
        print("Operator connected")

        await ws.send(json.dumps({
            "type": "clients",
            "clients": list(clients.keys())
        }))

    elif role == "client":

        client_id = str(uuid.uuid4())[:8]

        clients[client_id] = ws

        print("Client connected", client_id)

        if operator:
            await operator.send(json.dumps({
                "type": "new_client",
                "client_id": client_id
            }))

    try:

        async for message in ws:

            data = json.loads(message)

            if role == "client":

                if operator:
                    await operator.send(json.dumps({
                        "type": "message",
                        "client_id": client_id,
                        "text": data["text"]
                    }))

            elif role == "operator":

                target = data["client_id"]

                if target in clients:

                    await clients[target].send(json.dumps({
                        "type": "reply",
                        "text": data["text"]
                    }))

    except:
        pass

    finally:

        if role == "client":

            del clients[client_id]

            if operator:
                await operator.send(json.dumps({
                    "type": "client_left",
                    "client_id": client_id
                }))

        if ws == operator:
            operator = None


async def main():

    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Server started")
        await asyncio.Future()


asyncio.run(main())
