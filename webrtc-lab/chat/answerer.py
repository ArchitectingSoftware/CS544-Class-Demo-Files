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
    logger = setup_logger("answerer")
    log_protocol(logger, 'info', 'INIT', 'Starting WebRTC Answerer')
    
    # Wait for offer
    print("📥 Waiting for offer.json...")
    log_protocol(logger, 'info', 'SIGNALING', 'Waiting for offer.json')
    
    while not os.path.exists("offer.json"):
        await asyncio.sleep(1)

    log_protocol(logger, 'info', 'SIGNALING', 'Offer file detected')
    with open("offer.json", "r") as f:
        offer = json.load(f)
    
    # Log the received offer SDP
    log_protocol(logger, 'debug', 'SDP', f'Received offer SDP:\n{offer["sdp"]}')

    # Create peer connection
    pc = RTCPeerConnection()
    log_protocol(logger, 'info', 'RTC', 'PeerConnection created')
    
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

    @pc.on("datachannel")
    def on_datachannel(channel):
        log_protocol(logger, 'info', 'DATACHANNEL', f'Data channel received: {channel.label}')
        print("🟢 Data channel received. Type messages. Type 'exit' to quit.")

        @channel.on("message")
        async def on_message(message):
            log_protocol(logger, 'debug', 'DATACHANNEL', f'Received message: {message}')
            if message == "exit":
                log_protocol(logger, 'info', 'DATACHANNEL', 'Peer requested exit')
                print("\n🚪 Peer ended the chat.")
                await pc.close()
            else:
                print(f"\n[Offerer] Peer: {message}")
                print("[Answerer] You: ", end='', flush=True)
                
        @channel.on("close")
        async def on_close():
            log_protocol(logger, 'info', 'DATACHANNEL', 'Data channel closed')
            print("🔌 Connection closed by peer.")
            os._exit(0)

        async def user_input_loop():
            while True:
                msg = await asyncio.get_event_loop().run_in_executor(None, input, "[Answerer] You: ")
                if msg.strip().lower() == "exit":
                    log_protocol(logger, 'info', 'DATACHANNEL', 'User requested exit')
                    channel.send("exit")
                    await pc.close()
                    break
                log_protocol(logger, 'debug', 'DATACHANNEL', f'Sending message: {msg}')
                channel.send(msg)

        asyncio.create_task(user_input_loop())

    # Set remote description (offer)
    await pc.setRemoteDescription(RTCSessionDescription(**offer))
    log_protocol(logger, 'info', 'SDP', 'Remote description (offer) set')
    
    # Create and set local description (answer)
    log_protocol(logger, 'info', 'SDP', 'Creating answer')
    answer = await pc.createAnswer()
    log_protocol(logger, 'debug', 'SDP', f'Created answer SDP:\n{answer.sdp}')
    
    await pc.setLocalDescription(answer)
    log_protocol(logger, 'info', 'SDP', 'Local description (answer) set')

    # Write answer to file
    with open("answer.json", "w") as f:
        json.dump(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}, f
        )
    log_protocol(logger, 'info', 'SIGNALING', 'Answer written to answer.json')
    print("📤 Answer written to answer.json")

    # Keep the connection alive
    while pc.connectionState != "closed":
        await asyncio.sleep(1)

    log_protocol(logger, 'info', 'RTC', 'Connection closed, exiting')

if __name__ == "__main__":
    asyncio.run(main())