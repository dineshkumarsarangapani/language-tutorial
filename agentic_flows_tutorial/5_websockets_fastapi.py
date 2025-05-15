# 5. Event-Driven Concepts for Agents (WebSockets in FastAPI)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse # For a simple test client
from typing import List, Dict, Any
import asyncio
import datetime
import random

app = FastAPI(title="FastAPI WebSockets for Agentic Flows")

# --- What are WebSockets? ---
# WebSockets provide a full-duplex communication channel over a single TCP connection.
# This means both the client and server can send messages to each other independently
# and in real-time, after an initial handshake.

# --- Why use WebSockets for Agents? ---
# - **Interactive Communication:** Ideal for chatbots, real-time command/control of agents.
# - **Streaming Responses:** Agents can send back partial results or continuous updates as they process information.
# - **Real-time Notifications:** Servers (or agents) can push updates to clients without the client needing to poll.
# - **Reduced Latency:** Lower overhead compared to repeated HTTP requests for frequent small messages.

# --- Simple HTML Test Client (for demonstration) ---
# This HTML can be served by another endpoint or opened as a local file in a browser.
html_client_page = """
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI WebSocket Agent Test</title>
    </head>
    <body>
        <h1>WebSocket Agent Interaction</h1>
        <div>
            <label for="agentId">Agent ID (optional):</label>
            <input type="text" id="agentId" autocomplete="off" value="agent_007"/>
        </div>
        <div>
            <label for="messageText">Message to Agent:</label>
            <input type="text" id="messageText" autocomplete="off"/>
            <button onclick="sendMessage(event)">Send</button>
        </div>
        <h2>Agent Responses:</h2>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;
            function connect(event) {
                var agentId = document.getElementById("agentId").value;
                var url = `ws://localhost:8000/ws/chat/${agentId}`;
                if (!agentId) {
                    url = "ws://localhost:8000/ws/echo"; // Fallback to echo if no ID
                }
                console.log("Attempting to connect to: " + url);
                ws = new WebSocket(url);
                ws.onopen = function(event) {
                    var item = document.createElement('li');
                    item.innerHTML = "<i>Connection opened.</i>";
                    document.getElementById('messages').appendChild(item);
                };
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode("Agent: " + event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                ws.onclose = function(event) {
                    var item = document.createElement('li');
                    item.innerHTML = "<i>Connection closed.</i>";
                    document.getElementById('messages').appendChild(item);
                    ws = null;
                };
                ws.onerror = function(event) {
                    var item = document.createElement('li');
                    item.innerHTML = "<i>Error: " + JSON.stringify(event) + "</i>";
                    document.getElementById('messages').appendChild(item);
                };
            }
            function sendMessage(event) {
                if (!ws) {
                    alert("Not connected. Please connect first (usually happens automatically or refresh).");
                    return;
                }
                var input = document.getElementById("messageText")
                ws.send(input.value)
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode("You: " + input.value)
                message.appendChild(content)
                messages.appendChild(message)
                input.value = ''
                event.preventDefault()
            }
            // Attempt to connect on load
            window.onload = function() { connect(); };
        </script>
    </body>
</html>
"""

@app.get("/test-agent-client")
async def get_test_client_page():
    return HTMLResponse(html_client_page)

# --- Simple Echo WebSocket Endpoint ---
# This endpoint will simply echo back any message it receives.
@app.websocket("/ws/echo")
async def websocket_echo_endpoint(websocket: WebSocket):
    await websocket.accept() # Accept the WebSocket connection
    print("Echo WS: Client connected.")
    try:
        while True:
            data = await websocket.receive_text() # Wait for a message from the client
            print(f"Echo WS: Received from client: '{data}'")
            await websocket.send_text(f"Echo: You wrote '{data}'")
    except WebSocketDisconnect:
        print("Echo WS: Client disconnected.")
    except Exception as e:
        print(f"Echo WS: Error - {e}")
        await websocket.close(code=1011) # Internal error

# --- More Agent-like WebSocket Endpoint ---
# This simulates a simple conversational agent.

class ConnectionManager:
    """Manages active WebSocket connections for agents."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        print(f"Agent WS ({agent_id}): Connected.")

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            # await self.active_connections[agent_id].close() # Client usually initiates close
            del self.active_connections[agent_id]
            print(f"Agent WS ({agent_id}): Disconnected.")

    async def send_personal_message(self, message: str, agent_id: str):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_text(message)

    async def broadcast(self, message: str): # Example for broadcasting to all connected agents
        for agent_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Broadcast error to {agent_id}: {e}")

manager = ConnectionManager()

async def agent_logic_handler(agent_id: str, received_message: str, websocket: WebSocket):
    """Simulates the agent's response logic."""
    print(f"Agent ({agent_id}): Received '{received_message}'. Processing...")
    response_prefix = f"Agent ({agent_id}) thought about '{received_message}' and says: "
    
    await websocket.send_text(f"{response_prefix} Let me think...")
    await asyncio.sleep(random.uniform(0.5, 1.5)) # Simulate thinking time

    if "hello" in received_message.lower() or "hi" in received_message.lower():
        await websocket.send_text(f"{response_prefix} Hello there! How can I help you today?")
    elif "time" in received_message.lower():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await websocket.send_text(f"{response_prefix} The current time is {current_time}.")
    elif "weather" in received_message.lower():
        await websocket.send_text(f"{response_prefix} I can't fetch real weather yet, but it's probably nice!")
        await asyncio.sleep(0.5)
        await websocket.send_text("Agent is now simulating a tool call... (not really)")
    elif "bye" in received_message.lower():
        await websocket.send_text(f"{response_prefix} Goodbye! Have a great day.")
        # Optionally, the server could close the connection here or wait for client to close
        # await websocket.close()
        # manager.disconnect(agent_id)
    else:
        random_responses = [
            "That's interesting! Tell me more.",
            "I'm not sure I understand. Could you rephrase?",
            "Processing that... one moment.",
            "Let me consult my knowledge base for that."
        ]
        await websocket.send_text(f"{response_prefix} {random.choice(random_responses)}")
    
    # Example of agent sending a follow-up message unprompted
    if random.random() < 0.2: # 20% chance of a follow-up
        await asyncio.sleep(2)
        await websocket.send_text(f"Agent ({agent_id}): By the way, did you know I can also tell jokes? (not really yet)")

@app.websocket("/ws/chat/{agent_id}")
async def websocket_agent_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(agent_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await agent_logic_handler(agent_id, data, websocket)
            # Example: broadcast to other agents (if needed for your use case)
            # await manager.broadcast(f"Agent {agent_id} said: {data}") 
    except WebSocketDisconnect:
        manager.disconnect(agent_id)
    except Exception as e:
        print(f"Agent WS ({agent_id}): Error - {e}")
        manager.disconnect(agent_id)
        # await websocket.close(code=1011) # Ensure connection is closed if not already

# --- How to Run This Example ---
# 1. Save as a Python file (e.g., main_ws.py)
# 2. Run with Uvicorn: `uvicorn agentic_flows_tutorial.5_websockets_fastapi:app --reload --port 8000`
# 3. Open your browser to http://127.0.0.1:8000/test-agent-client
#    - This page provides a basic UI to connect to `/ws/chat/{agent_id}` or `/ws/echo`.
#    - Enter an agent ID (e.g., "user123") or leave blank for echo.
#    - Send messages and observe the agent's responses.
# 4. Alternatively, use a dedicated WebSocket client tool like `websocat`:
#    For echo: `websocat ws://localhost:8000/ws/echo`
#    For agent chat: `websocat ws://localhost:8000/ws/chat/my_agent_session`
#    Then type messages and press Enter.

print("--- FastAPI with WebSockets for Agentic Flows ---")
print("This app demonstrates real-time bidirectional communication using WebSockets.")
print("Run with: uvicorn filename:app --reload (e.g., uvicorn 5_websockets_fastapi:app --reload)")
print("Access the test client at http://localhost:8000/test-agent-client") 