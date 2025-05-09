#!/usr/bin/env python3
"""
WebRTC Log Analyzer
-------------------
A tool to analyze and visualize WebRTC protocol interactions from log files.

Usage:
    python webrtc_log_analyzer.py offerer_webrtc.log answerer_webrtc.log --output webrtc_timeline.html
"""

import argparse
import re
import json
import datetime
from collections import defaultdict

def parse_log_file(log_file):
    """Parse a WebRTC log file and extract protocol events."""
    events = []
    
    time_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})'
    protocol_pattern = r'\| (\w+) \|'  # This captures the log level
    proto_pattern = r'\| (\w+) \|'     # This will capture our custom protocol field
    
    with open(log_file, 'r') as f:
        for line in f:
            # Extract timestamp
            time_match = re.search(time_pattern, line)
            if not time_match:
                continue
            
            timestamp = time_match.group(1)
            
            # Extract log level (3rd field)
            level_match = re.search(protocol_pattern, line)
            if not level_match:
                continue
            
            # Extract protocol field (4th field)
            proto_parts = line.split('|')
            if len(proto_parts) < 5:
                continue
            
            protocol = proto_parts[3].strip()
            
            # Extract message (everything after the protocol - 5th field)
            message = proto_parts[4].strip()
            
            # Parse timestamp
            dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f')
            
            events.append({
                'timestamp': dt,
                'protocol': protocol,
                'message': message,
                'source': log_file.split('_')[0]  # Extract source (offerer/answerer)
            })
    
    return events

def generate_timeline_html(events, output_file):
    """Generate an HTML timeline visualization of WebRTC events."""
    # Sort events by timestamp
    events.sort(key=lambda x: x['timestamp'])
    
    # Group events by protocol
    protocols = defaultdict(list)
    for event in events:
        protocols[event['protocol']].append(event)
    
    # Create HTML file
    with open(output_file, 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebRTC Protocol Timeline</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .timeline { position: relative; margin: 20px 0; padding: 20px 0; }
                .timeline::before { content: ''; position: absolute; top: 0; bottom: 0; width: 4px; background: #ddd; left: 50%; margin-left: -2px; }
                .timeline-item { padding: 10px 40px; position: relative; background-color: inherit; width: 46%; }
                .left { left: 0; }
                .right { left: 50%; }
                .timeline-item::after { content: ''; position: absolute; width: 16px; height: 16px; right: -8px; background-color: white; border: 4px solid #FF9F55; top: 15px; border-radius: 50%; z-index: 1; }
                .right::after { left: -8px; }
                .timeline-content { padding: 20px; background-color: white; border-radius: 6px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                .protocol-filter { margin: 20px 0; }
                .protocol-filter button { margin-right: 10px; padding: 5px 10px; border: none; border-radius: 3px; background-color: #eee; cursor: pointer; }
                .protocol-filter button.active { background-color: #FF9F55; color: white; }
                .timestamp { color: #999; font-size: 0.8em; }
                .message { margin-top: 5px; }
                .source-offerer { border-left: 5px solid #4CAF50; }
                .source-answerer { border-left: 5px solid #2196F3; }
                .hidden { display: none; }
                .legend { margin-top: 20px; display: flex; }
                .legend-item { margin-right: 20px; display: flex; align-items: center; }
                .legend-color { width: 20px; height: 20px; margin-right: 5px; }
                .offerer-color { background-color: #4CAF50; }
                .answerer-color { background-color: #2196F3; }
                h3 { margin-bottom: 5px; }
                .protocol-heading { display: flex; justify-content: space-between; align-items: center; }
                .protocol-badge { padding: 2px 6px; border-radius: 10px; color: white; font-size: 0.8em; }
                .protocol-SDP { background-color: #673AB7; }
                .protocol-ICE { background-color: #3F51B5; }
                .protocol-DTLS { background-color: #009688; }
                .protocol-SCTP { background-color: #FF5722; }
                .protocol-RTP { background-color: #795548; }
                .protocol-DATACHANNEL { background-color: #607D8B; }
                .protocol-SIGNALING { background-color: #9C27B0; }
                .protocol-RTC { background-color: #E91E63; }
                .protocol-GENERAL { background-color: #9E9E9E; }
                .timeline-item-details { display: none; margin-top: 10px; }
                .show-details-btn { background: none; border: none; text-decoration: underline; color: blue; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>WebRTC Protocol Timeline</h1>
            
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color offerer-color"></div>
                    <div>Offerer</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color answerer-color"></div>
                    <div>Answerer</div>
                </div>
            </div>
            
            <div class="protocol-filter">
                <button class="filter-btn active" data-protocol="all">All</button>
        """)
        
        # Add filter buttons for each protocol
        for protocol in sorted(protocols.keys()):
            f.write(f'<button class="filter-btn" data-protocol="{protocol}">{protocol}</button>\n')
        
        f.write("""
            </div>
            
            <div class="timeline">
        """)
        
        # Add timeline items
        for i, event in enumerate(events):
            side = "left" if i % 2 == 0 else "right"
            timestamp = event['timestamp'].strftime('%H:%M:%S.%f')[:-3]
            source = event['source']
            protocol = event['protocol']
            message = event['message']
            
            # Handle SDP content - collapse long content and add show/hide button
            details = ""
            if protocol == "SDP" and "\n" in message:
                # Split into summary and details
                summary, *content = message.split("\n", 1)
                details = content[0] if content else ""
                message = summary
            
            f.write(f"""
                <div class="timeline-item {side} data-protocol="{protocol}">
                    <div class="timeline-content source-{source}">
                        <div class="protocol-heading">
                            <h3>{protocol}</h3>
                            <span class="protocol-badge protocol-{protocol}">{protocol}</span>
                        </div>
                        <div class="timestamp">{timestamp} - {source}</div>
                        <div class="message">{message}</div>
                        """)
            
            # Add details section if needed
            if details:
                f.write(f"""
                        <button class="show-details-btn" onclick="toggleDetails(this)">Show SDP details</button>
                        <div class="timeline-item-details">
                            <pre>{details}</pre>
                        </div>
                        """)
            
            f.write("""
                    </div>
                </div>
            """)
        
        f.write("""
            </div>
            
            <script>
                // Filter events by protocol
                document.querySelectorAll('.filter-btn').forEach(button => {
                    button.addEventListener('click', () => {
                        // Update active button
                        document.querySelectorAll('.filter-btn').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        button.classList.add('active');
                        
                        const protocol = button.dataset.protocol;
                        
                        // Show/hide timeline items
                        document.querySelectorAll('.timeline-item').forEach(item => {
                            if (protocol === 'all' || item.dataset.protocol === protocol) {
                                item.classList.remove('hidden');
                            } else {
                                item.classList.add('hidden');
                            }
                        });
                    });
                });
                
                // Toggle SDP details
                function toggleDetails(button) {
                    const details = button.nextElementSibling;
                    if (details.style.display === 'block') {
                        details.style.display = 'none';
                        button.textContent = 'Show SDP details';
                    } else {
                        details.style.display = 'block';
                        button.textContent = 'Hide SDP details';
                    }
                }
            </script>
        </body>
        </html>
        """)
    
    print(f"Timeline visualization created: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Analyze WebRTC protocol logs')
    parser.add_argument('log_files', nargs='+', help='WebRTC log files to analyze')
    parser.add_argument('--output', default='webrtc_timeline.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    # Parse log files
    all_events = []
    for log_file in args.log_files:
        events = parse_log_file(log_file)
        all_events.extend(events)
    
    # Generate timeline visualization
    generate_timeline_html(all_events, args.output)

if __name__ == "__main__":
    main()