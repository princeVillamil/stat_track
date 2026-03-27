from fastapi import WebSocket
import asyncio


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    Why a class? Because you need shared state across requests.
    A plain dict would work but a class gives you clean methods
    and a single place to handle all connection logic.
    """

    def __init__(self):
        # dict of region → list of connected WebSockets
        # grouped by region so you only push NAmerica updates
        # to clients watching NAmerica
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, region: str):
        """Accept a new connection and register it."""
        await websocket.accept()

        if region not in self.active:
            self.active[region] = []

        self.active[region].append(websocket)
        print(f"Client connected to {region}. "
              f"Total connections: {self._total()}")

    def disconnect(self, websocket: WebSocket, region: str):
        """Remove a connection when client disconnects."""
        if region in self.active:
            self.active[region].remove(websocket)
        print(f"Client disconnected from {region}. "
              f"Total connections: {self._total()}")

    async def broadcast_to_region(self, region: str, message: dict):
        """
        Send a message to all clients watching a specific region.
        Handles disconnected clients gracefully.
        """
        if region not in self.active:
            return

        # iterate over a copy — we may remove items during iteration
        dead_connections = []

        for websocket in self.active[region].copy():
            try:
                await websocket.send_json(message)
            except Exception:
                # client disconnected without clean close
                # mark for removal — don't remove during iteration
                dead_connections.append(websocket)

        # clean up dead connections
        for websocket in dead_connections:
            self.active[region].remove(websocket)

    def _total(self) -> int:
        return sum(len(conns) for conns in self.active.values())


# single shared instance — imported by both the router and the Redis listener
manager = ConnectionManager()