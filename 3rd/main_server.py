import asyncio
import os

HOST = "0.0.0.0"
PORT = 5002
DELIMITER = "<SEP>"
chat_rooms = {}


async def client_session(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"[+] Connection established with {address}.")
    active_room = None

    try:
        while True:
            incoming = await reader.read(1024)
            if not incoming:
                break
            command = incoming.decode().strip()

            if command.startswith("/join"):
                room = command.split(" ", 1)[-1].strip()
                if active_room:
                    chat_rooms[active_room].discard(writer)
                    if not chat_rooms[active_room]:
                        del chat_rooms[active_room]
                active_room = room
                chat_rooms.setdefault(active_room, set())
                if active_room.startswith("private_") and len(chat_rooms[active_room]) >= 2:
                    writer.write("[ERROR] Private room limit reached.\n".encode())
                else:
                    chat_rooms[active_room].add(writer)
                    writer.write(f"[INFO] Entered room: {active_room}\n".encode())
                await writer.drain()
                continue

            if not active_room:
                writer.write("[ERROR] Please join a room first using /join <room_name>.\n".encode())
                await writer.drain()
                continue

            if command.startswith("/sendfile"):
                _, filename = command.split(" ", 1)
                writer.write(f"[INFO] Preparing to upload file: {filename}\n".encode())
                await writer.drain()

                os.makedirs("uploads", exist_ok=True)
                file_path = os.path.join("uploads", filename)
                with open(file_path, "wb") as file:
                    while True:
                        data = await reader.read(1024)
                        if data.endswith(b"<EOF>"):
                            file.write(data[:-5])
                            break
                        file.write(data)

                writer.write("[INFO] File received successfully.\n".encode())
                await writer.drain()

                # Forward the file to room members
                for client in chat_rooms[active_room]:
                    if client == writer:
                        continue
                    try:
                        client.write(f"/file {filename}\n".encode())
                        await client.drain()
                        with open(file_path, "rb") as file:
                            while chunk := file.read(1024):
                                client.write(chunk)
                                await client.drain()
                        client.write(b"<EOF>")
                        await client.drain()
                    except Exception as err:
                        print(f"[ERROR] Unable to forward file: {err}")
                continue

            # Send message to all participants in the room
            broadcast_message = f"{command.replace(DELIMITER, ': ')}"
            print(f"Room {active_room}: {broadcast_message.strip()}")
            for participant in chat_rooms[active_room]:
                if participant != writer:
                    participant.write(broadcast_message.encode())
                    await participant.drain()

    except Exception as err:
        print(f"[!] An error occurred with {address}: {err}")
    finally:
        if active_room and writer in chat_rooms.get(active_room, set()):
            chat_rooms[active_room].discard(writer)
            if not chat_rooms[active_room]:
                del chat_rooms[active_room]
        print(f"[-] Connection closed for {address}.")
        writer.close()
        await writer.wait_closed()


async def start_server():
    server = await asyncio.start_server(client_session, HOST, PORT)
    server_addr = server.sockets[0].getsockname()
    print(f"[*] Server running on {server_addr[0]}:{server_addr[1]}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n[!] Server has been terminated.")
