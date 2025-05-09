# WebRTC Exploration Lab

## Introduction

WebRTC (Web Real-Time Communication) enables direct peer-to-peer communication in browsers without plugins or server intermediaries. This lab will guide you through exploring WebRTC's core components and protocols using working code samples.

The lab uses Python with the `aiortc` library, which implements the WebRTC specification. By examining and running the provided code, you'll gain hands-on experience with WebRTC's key mechanisms.

## WebRTC Protocol Overview

Before diving into the code, let's understand the key components of the WebRTC protocol stack:

1. **Signaling**: Exchange of session information between peers (not standardized in WebRTC)
2. **ICE (Interactive Connectivity Establishment)**: NAT traversal to establish peer connections
3. **STUN/TURN**: Services that help with NAT traversal
4. **DTLS (Datagram TLS)**: Secures the connection
5. **SCTP (Stream Control Transmission Protocol)**: Provides data channels
6. **SRTP (Secure Real-time Transport Protocol)**: Encrypts media streams

The typical WebRTC connection flow is:
- Exchange offers/answers via signaling
- Gather and exchange ICE candidates
- Establish secure connection with DTLS
- Set up data channels (SCTP) or media streams (SRTP)

## Lab Setup

### Prerequisites

- Python 3.7+
- Required packages:
  ```
  aiortc>=1.3.0
  aiohttp>=3.8.1
  numpy>=1.20.0
  opencv-python>=4.5.0
  av>=9.0.0
  ```

### Installation

```bash
pip install -r requirements.txt
```

## Part 1: Data Channel Communication (Offerer/Answerer)

The `offerer.py` and `answerer.py` scripts implement a simple WebRTC data channel chat application. These scripts demonstrate the core WebRTC connection establishment process.

### Key Code Components to Understand

**1. RTCPeerConnection Initialization**

In both scripts, a peer connection is created:
```python
pc = RTCPeerConnection()
```

**2. Data Channel Creation**

In `offerer.py`, a data channel is explicitly created:
```python
channel = pc.createDataChannel("chat")
```

In `answerer.py`, the data channel is received through an event:
```python
@pc.on("datachannel")
def on_datachannel(channel):
    # Handle incoming data channel
```

**3. Offer/Answer Creation**

In `offerer.py`:
```python
offer = await pc.createOffer()
await pc.setLocalDescription(offer)
```

In `answerer.py`:
```python
await pc.setRemoteDescription(RTCSessionDescription(**offer))
answer = await pc.createAnswer()
await pc.setLocalDescription(answer)
```

**4. Signaling**

These scripts use files for signaling:
- `offer.json`: Created by offerer, read by answerer
- `answer.json`: Created by answerer, read by offerer

**5. ICE Handling**

Both scripts monitor ICE events:
```python
@pc.on("iceconnectionstatechange")
async def on_iceconnectionstatechange():
    # Monitor ICE connection state
```

**6. Logging**

Custom logging captures protocol-specific events:
```python
log_protocol(logger, 'info', 'ICE', f"ICE connection state changed to: {pc.iceConnectionState}")
```

### Lab Task 1: Running the Data Channel Demo

#### 1.1 Examine the Code
First, carefully review both `offerer.py` and `answerer.py` to understand how they implement WebRTC concepts.

#### 1.2 Run the Chat Demo

1. In terminal window 1:
   ```
   python offerer.py
   ```

2. In terminal window 2:
   ```
   python answerer.py
   ```

3. Exchange messages between the terminals. The offerer initiates the connection, and once established, both sides can send messages.

4. Type "exit" to close the connection.

#### 1.3 What to Look For

1. **Console Output**: 
   - Notice the sequence of events: offer creation, ICE gathering, answer reception, connection establishment
   - Observe timing between different stages

2. **Log Files**:
   - After running the demo, examine `offerer_webrtc.log` and `answerer_webrtc.log`
   - Look for protocol markers like INIT, SDP, ICE, DATACHANNEL

3. **Protocol Flow**:
   - Notice how the connection moves through different states
   - Identify the point when secure communication is established

#### 1.4 Questions to Explore

- How long does it take from offer creation to connection establishment?
- What ICE candidates are generated and exchanged?
- What steps happen before the data channel becomes usable?

## Part 2: Analyzing the Connection Logs

The `loganalysis.py` script creates a visualization of the WebRTC connection process based on the logs generated during your chat session.

### Key Components of the Log Analyzer

1. **Log Parsing**:
   ```python
   def parse_log_file(log_file):
       # Extract timestamp, protocol, message from logs
   ```

2. **Timeline Generation**:
   ```python
   def generate_timeline_html(events, output_file):
       # Create visual timeline of WebRTC events
   ```

3. **Protocol Filtering**:
   The HTML output includes buttons to filter events by protocol.

### Lab Task 2: Visualizing the Protocol Flow

#### 2.1 Run the Log Analyzer

```
python loganalysis.py offerer_webrtc.log answerer_webrtc.log --output webrtc_timeline.html
```

#### 2.2 Examine the Timeline

Open `webrtc_timeline.html` in a browser and explore the visualization:

1. Use the protocol filter buttons to focus on specific protocols
2. Notice the sequence and timing of events
3. Examine SDP content (click "Show SDP details")

#### 2.3 What to Look For

1. **Protocol Sequence**:
   - INIT → SDP → ICE → RTC → DATACHANNEL
   - Note the order and dependencies between protocols

2. **SDP Analysis**:
   - Examine offer and answer SDP content
   - Look for ICE credentials (`ice-ufrag`, `ice-pwd`)
   - Find DTLS fingerprints (`fingerprint:sha-256`)
   - Locate SCTP parameters (`sctpmap`, `max-message-size`)

3. **ICE Process**:
   - ICE gathering state transitions
   - Candidate generation
   - Connection state changes

4. **DTLS and Security**:
   - When does the secure handshake happen?
   - What fingerprints are exchanged?

#### 2.4 Questions to Explore

- What is the complete sequence of protocols in a successful WebRTC connection?
- How do the offerer and answerer roles differ in the connection process?
- What security mechanisms are visible in the logs?
- How much time is spent in each phase of the connection?

## Part 3: WebRTC Video Streaming

The `video-webrtc.py` script implements a WebRTC server that streams dynamically generated video. This demonstrates media handling in WebRTC.

### Key Components of the Video Streaming Demo

1. **Custom Video Stream**:
   ```python
   class TestVideoStreamTrack(MediaStreamTrack):
       # Generates test video pattern
   ```

2. **Offer Handling**:
   ```python
   async def offer_handler(request):
       # Process incoming WebRTC offers
   ```

3. **Media Track Addition**:
   ```python
   pc.addTrack(TestVideoStreamTrack())
   ```

4. **Web Server Integration**:
   ```python
   app = web.Application()
   app.router.add_post("/offer", offer_handler)
   ```

### Lab Task 3: Exploring Video Streaming

#### 3.1 Run the Video Streaming Server

```
python video-webrtc.py
```

#### 3.2 Connect to the Video Stream

1. Open a web browser and navigate to `http://localhost:9080`
2. Click "Start" to initiate the WebRTC connection
3. Observe the video pattern stream

#### 3.3 What to Look For

1. **Browser Dev Tools**:
   - Open Chrome DevTools or Firefox WebRTC internals
   - Look for WebRTC related events
   - Observe ICE candidate gathering

2. **Server Console**:
   - Notice log entries for connection establishment
   - Observe media-related messages

3. **Video Stream Behavior**:
   - Note frame rate and resolution
   - Observe the pattern change over time

#### 3.4 Key Differences from Data Channel Demo

- SDP contains additional media sections (`m=video`)
- Video codec negotiation happens in SDP
- SRTP is used for secure media transmission
- Additional statistics available for media quality

#### 3.5 Questions to Explore

- How does the SDP for video streaming differ from data-only WebRTC?
- What additional protocols are involved with media streaming?
- How is the frame rate controlled in the implementation?
- What parameters could you adjust to change video quality?

## Part 4: Code Exploration Challenges

Now that you've seen the demos in action, let's explore the code more deeply to understand specific WebRTC mechanisms:

### 4.1 SDP Examination

Find the sections in the code where SDP is:
1. Created
2. Processed
3. Modified (if applicable)

Questions:
- What key information is contained in the SDP?
- How does the SDP differ between offer and answer?
- Where are media capabilities negotiated?

### 4.2 ICE Implementation

Locate the ICE-related code:
1. Find ICE candidate gathering
2. Identify ICE state transitions
3. Locate where candidates are processed

Questions:
- How are ICE candidates generated?
- What happens when the ICE state changes?
- How are remote ICE candidates processed?

### 4.3 Data Channel vs. Media Track

Compare the implementation of:
1. Data channel creation and handling
2. Media track creation and transmission

Questions:
- What are the key differences between data and media handling?
- How is reliability configured for data channels?
- How are media frames generated and timed?

### 4.4 Security Implementation

Find the security-related code:
1. Locate DTLS parameters
2. Identify certificate handling
3. Find encryption configuration

Questions:
- How are certificates or fingerprints generated?
- How is the secure connection established?
- What encryption is used for data vs. media?

## Part 5: Hands-on Challenges (Optional)

Now that you understand the core WebRTC mechanics, try these modifications to deepen your understanding:

### 5.1 Data Channel Enhancements

Pick one to implement:
1. Add message timestamps
2. Implement basic text formatting
3. Add support for user nicknames
4. Create a system for "typing" indicators

### 5.2 Video Stream Modifications

Try one of these:
1. Change the video resolution or frame rate
2. Modify the test pattern to include custom text
3. Add a clock or timer overlay
4. Implement a color filter effect

### 5.3 Connection Analysis Enhancements

Improve the log analyzer:
1. Add timing statistics between protocols
2. Create a visualization of ICE candidate types
3. Add SDP comparison features
4. Generate a simplified protocol timeline chart

## WebRTC Protocol Reference

As you work through the lab tasks, refer to this guide to understand the protocols you'll encounter in the logs:

### SDP (Session Description Protocol)
- **Purpose**: Describes session metadata and media capabilities
- **Log Markers**: `SDP` protocol
- **Key Content**: Media types, codecs, transport, security parameters
- **Pattern**: Always follows offer/answer model

### ICE (Interactive Connectivity Establishment)
- **Purpose**: NAT traversal to establish peer connections
- **Log Markers**: `ICE` protocol
- **Key States**: "new", "gathering", "checking", "connected", "completed"
- **Pattern**: Gathering → candidates exchange → connectivity checks

### RTC (Core WebRTC Connection)
- **Purpose**: Overall connection management
- **Log Markers**: `RTC` protocol
- **Key States**: "new", "connecting", "connected", "disconnected", "closed"
- **Pattern**: Follows ICE state progression with additional validation

### DATACHANNEL
- **Purpose**: Bidirectional data communication
- **Log Markers**: `DATACHANNEL` protocol
- **Key Events**: Channel creation, opening, messages, closing
- **Pattern**: Created → negotiated → opened → message exchange → closed

### DTLS (Datagram Transport Layer Security)
- **Purpose**: Connection security
- **Not explicitly logged**, but visible in SDP as fingerprints
- **Key Content**: Certificate fingerprints
- **Pattern**: Handshake follows ICE connection

### SRTP (Secure Real-time Transport Protocol)
- **Purpose**: Encrypted media transport
- **Not explicitly logged**, but used for video/audio
- **Key Content**: Encryption derived from DTLS
- **Pattern**: Established after DTLS completes

## Summary

This lab has guided you through exploring WebRTC's key components:
1. Connection establishment with signaling and ICE
2. Secure communication with DTLS
3. Data channel communication over SCTP
4. Media streaming with SRTP
5. Log analysis and protocol visualization

By working with real code and seeing the protocols in action, you've gained practical insights into how WebRTC enables secure, real-time communication across the web.

## Further Resources

- [WebRTC for the Curious](https://webrtcforthecurious.com/)
- [MDN WebRTC API documentation](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [aiortc Documentation](https://aiortc.readthedocs.io/)
