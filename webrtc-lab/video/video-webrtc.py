import argparse
import asyncio
import logging
import os
import json
import time
from fractions import Fraction
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaRelay
from av import VideoFrame
import numpy as np
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webrtc-transport-demo")

# Keep track of active peer connections
pcs = set()
relay = MediaRelay()

# Custom video track that generates a test pattern
class TestVideoStreamTrack(MediaStreamTrack):
    kind = "video"
    
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.width = 640
        self.height = 480
        self.pts = 0
        self.time_base = Fraction(1, 30)  # 30 fps as a rational number
        self._start = time.time()
    
    async def next_timestamp(self):
        """
        Calculate the next timestamp for frame timing.
        """
        if self.counter == 0:
            self.pts = 0
        else:
            self.pts = int((time.time() - self._start) / float(self.time_base))
        return self.pts, self.time_base
    
    async def recv(self):
        self.counter += 1
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Create a color pattern
        for y in range(self.height):
            for x in range(self.width):
                img[y, x, 0] = (x + self.counter) % 256  # Blue
                img[y, x, 1] = (y + self.counter) % 256  # Green
                img[y, x, 2] = ((x + y + self.counter) // 2) % 256  # Red
        
        # Add frame counter
        cv2.putText(
            img,
            f"Frame {self.counter}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )
        
        # Convert to VideoFrame
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        return frame

async def index(request):
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r") as f:
        content = f.read()
    return web.Response(content_type="text/html", text=content)

async def offer_handler(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    logger.info("Created RTCPeerConnection")
    logger.info(f"SDP offer type: {offer.type}")
    
    # Handle data channel
    @pc.on("datachannel")
    def on_datachannel(channel):
        logger.info(f"Data channel established: {channel.label}")
        
        @channel.on("message")
        def on_message(message):
            logger.info(f"Received message: {message}")
            channel.send(f"Echo: {message}")
    
    # Handle ICE connection state
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info(f"ICE connection state: {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed" or pc.iceConnectionState == "closed":
            await pc.close()
            pcs.discard(pc)
    
    # Set the remote description first
    await pc.setRemoteDescription(offer)
    logger.info("Set remote description")
    
    # Create video track and add it to peer connection
    pc.addTrack(TestVideoStreamTrack())
    logger.info("Added video track to peer connection")
    
    # Create data channel if one wasn't received
    if not pc.getTransceivers():
        pc.createDataChannel("chat")
    
    # Create answer
    answer = await pc.createAnswer()
    logger.info("Created answer")
    
    # Set local description
    await pc.setLocalDescription(answer)
    logger.info("Set local description")
    
    # Wait for ICE gathering to complete
    await asyncio.sleep(1)
    
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )

async def on_shutdown(app):
    # Close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC Transport Analysis Demo")
    parser.add_argument("--port", type=int, default=9080, help="Port for HTTP server (default: 9080)")
    args = parser.parse_args()

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer_handler)
    app.router.add_static("/", path=os.path.join(os.path.dirname(__file__), "static"))
    
    web.run_app(app, host="0.0.0.0", port=args.port)