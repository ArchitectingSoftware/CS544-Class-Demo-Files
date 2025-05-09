# WebRTC Lab and Asynchronous Assignment

### Introduction

WebRTC (Web Real-Time Communication) serves as an instructive example of application-layer protocol design that orchestrates multiple underlying protocols to enable peer-to-peer communication across the internet. Unlike traditional transport protocols focused on single concerns, WebRTC operates as a meta-protocol that coordinates ICE for NAT traversal, SDP for session negotiation, DTLS for security, SCTP for data channels, and RTP/SRTP for media streaming. This multi-protocol approach demonstrates how application-layer designs can abstract complexity while addressing real-world networking constraints like firewalls, NATs, and varying network conditions. By examining WebRTC, students observe how an application protocol makes intelligent decisions about connection paths, adapts to network limitations, provides fallback mechanisms, and maintains security throughout the communication process. The protocol's architecture illustrates key networking principles including protocol composition, signaling systems, and practical solutions to the asymmetric routing problems that characterize today's internet. WebRTC's design choices offer valuable insights into the tradeoffs and engineering decisions required when building modern communication systems on top of existing internet infrastructure.


### Directions

This is a self directed lab.  What you get out of it will be related to what you put into it. 

1. Start with learning about WebRTC using online resources.  You are free to self-discover and learn on your own.  You might even want to use a LLM such as ChatGPT or another and prompt it to teach you about this protocol.  In the study guide I am providing there is a section on online learning resources that I pulled together for you.  There are long videos, shorter ones, play lists, articles, etc.  There is no hard requirement, pick what works for you and run with it.  The main goal is to *"learn how to learn"* using the network foundation that we have been discussing in class.  I would not attempt the hands on lab until I at the minimum had some familiarity with the protocol suite itself.  Here is the link to the online resources that I have provided for you:  [WebRTC Online Learning Resources](https://github.com/ArchitectingSoftware/CS544-Class-Demo-Files/blob/main/webrtc-lab/webrtc-study-guide.md#online-learning-resources)

2. Once you have some working knowledge about WebRTC you will be ready to play with the code demo code.  Step by step directions and challenges are provided in the lab guide - open up [web-rtc-lab.md](./web-rtc-lab.md). This document provides you detailed directions on how to use the code that I provided along with some additional learning challenges.  Note that you will need python installed on your machine to run these programs.  If you dont have python on your machine, or have trouble getting it working, there are a lot of online resources out there to help you.

3. Now that you have done some self-directed learning its time to show me what you know - haha.  I have provided a study guide to help you prepare for the online quiz.   Open up and review [web-rtc-study-guide.md](./web-rtc-study-guide.md).  

