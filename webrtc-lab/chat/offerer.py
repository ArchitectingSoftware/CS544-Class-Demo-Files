import asyncio
import json
import os
import sys
import logging
import time
from aiortc import RTCPeerConnection, RTCSessionDescription


# Configure logging
def setup_logger(name):
    log_file = f"{name}_webrtc.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter - we use a custom field 'proto' to avoid conflict with LogRecord attributes
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(proto)s | %(message)s')
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Custom function to log with protocol type
def log_protocol(logger, level, protocol, message):
    logger_method = getattr(logger, level)
    logger_method(message, extra={'proto': protocol})

async def main():
    # Set up logging
    logger = setup_logger("offerer")
    log_protocol(logger, 'info', 'INIT', 'Starting WebRTC Offerer')
    
    pc = RTCPeerConnection()
    
    # Monitor and log ICE connection state changes
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_protocol(logger, 'info', 'ICE', f"ICE connection state changed to: {pc.iceConnectionState}")
        
    # Monitor and log connection state changes
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_protocol(logger, 'info', 'RTC', f"Connection state changed to: {pc.connectionState}")
    
    # Monitor and log ICE gathering state
    @pc.on("icegatheringstatechange")
    async def on_icegatheringstatechange():
        log_protocol(logger, 'info', 'ICE', f"ICE gathering state changed to: {pc.iceGatheringState}")
    
    # Log when ICE candidates are created
    @pc.on("icecandidate")
    def on_icecandidate(candidate):
        if candidate:
            log_protocol(logger, 'debug', 'ICE', f"New ICE candidate: {candidate.sdpMid} {candidate.sdpMLineIndex} {candidate.candidate}")
    
    # Create data channel
    log_protocol(logger, 'info', 'RTC', 'Creating data channel "chat"')
    channel = pc.createDataChannel("chat")

    @channel.on("open")
    def on_open():
        log_protocol(logger, 'info', 'DATACHANNEL', 'Data channel opened')
        print("💬 Data channel open. Type messages. Type 'exit' to quit.")

        async def user_input_loop():
            while True:
                msg = await asyncio.get_event_loop().run_in_executor(None, input, "[Offerer] You: ")
                if msg.strip().lower() == "exit":
                    log_protocol(logger, 'info', 'DATACHANNEL', 'User requested exit')
                    channel.send("exit")
                    await pc.close()
                    break
                log_protocol(logger, 'debug', 'DATACHANNEL', f'Sending message: {msg}')
                channel.send(msg)

        asyncio.create_task(user_input_loop())

    @channel.on("message")
    async def on_message(message):
        log_protocol(logger, 'debug', 'DATACHANNEL', f'Received message: {message}')
        if message == "exit":
            log_protocol(logger, 'info', 'DATACHANNEL', 'Peer requested exit')
            print("\n🚪 Peer ended the chat.")
            await pc.close()
        else:
            print(f"\n[Answerer] Peer: {message}")
            print("[Offerer] You: ", end='', flush=True)
            
    @channel.on("close")
    async def on_close():
        log_protocol(logger, 'info', 'DATACHANNEL', 'Data channel closed')
        print("🔌 Connection closed by peer.")
        os._exit(0)

    # Write offer to file
    if os.path.exists("offer.json"):
        os.remove("offer.json")
    if os.path.exists("answer.json"):
        os.remove("answer.json")

    # Create and set local description (offer)
    log_protocol(logger, 'info', 'SDP', 'Creating offer')
    offer = await pc.createOffer()
    log_protocol(logger, 'debug', 'SDP', f'Created offer SDP:\n{offer.sdp}')
    
    await pc.setLocalDescription(offer)
    log_protocol(logger, 'info', 'SDP', 'Local description (offer) set')
    
    # Write offer to file
    with open("offer.json", "w") as f:
        json.dump(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}, f
        )
    log_protocol(logger, 'info', 'SIGNALING', 'Offer written to offer.json')
    print("📤 Offer written to offer.json")
    print("📥 Waiting for answer.json...")

    # Wait for answer
    while not os.path.exists("answer.json"):
        await asyncio.sleep(1)

    log_protocol(logger, 'info', 'SIGNALING', 'Answer file detected')
    with open("answer.json", "r") as f:
        answer = json.load(f)

    # Log the received answer SDP
    log_protocol(logger, 'debug', 'SDP', f'Received answer SDP:\n{answer["sdp"]}')
    
    # Set remote description (answer)
    await pc.setRemoteDescription(RTCSessionDescription(**answer))
    log_protocol(logger, 'info', 'SDP', 'Remote description (answer) set')
    print("✅ Answer received. Connection should be established.")

    # Keep the connection alive
    while pc.connectionState != "closed":
        await asyncio.sleep(1)

    log_protocol(logger, 'info', 'RTC', 'Connection closed, exiting')

if __name__ == "__main__":
    asyncio.run(main())