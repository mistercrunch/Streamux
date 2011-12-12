#!/usr/bin/python
#Server
#gst-launch-0.10 filesrc location=test.mp3 ! mad ! audioconvert ! audio/x-raw-int,channels=2,depth=16,width=16, rate=44100 ! rtpL16pay  ! udpsink host=224.1.1.1 port=5000 auto-multicast=true 

#Client
#gst-launch-0.10 udpsrc auto-multicast=true multicast-group=224.1.1.1 port=5000 ! "application/x-rtp,media=(string)audio, clock-rate=(int)44100, width=16, height=16, encoding-name=(string)L16, encoding-params=(string)1, channels=(int)2, channel-positions=(int)1, payload=(int)96" ! gstrtpjitterbuffer do-lost=true ! rtpL16depay ! audioconvert ! alsasink
#Server
gst-launch-0.10 \
filesrc location=test.mp3 ! \
mad ! \
audioconvert ! \
"audio/x-raw-int,rate=44100,channels=2" !\
faac ! \
rtpmp4apay ! \
udpsink host=224.1.1.1 port=5000 auto-multicast=true sync=false

#Client
gst-launch-0.10 \
udpsrc auto-multicast=true multicast-group=224.1.1.1 port=5000 ! \
"application/x-rtp, media=(string)audio, clock-rate=(int)44100, encoding-name=(string)MP4A-LATM, cpresent=(string)0, config=(string)40002420, payload=(int)96, ssrc=(guint)746617717, clock-base=(guint)4130738665, seqnum-base=(guint)58682" ! \
gstrtpbin ! \
rtpmp4adepay ! \
"audio/mpeg,mpegversion=(int)4,channels=(int)2,rate=(int)44100" ! \
faad ! \
alsasink sync=false


#Server
gst-launch-0.10 \
filesrc location=test.mp3 ! \
mad ! \
audioconvert ! \
"audio/x-raw-int,rate=44100,channels=2" ! \
udpsink host=224.1.1.1 port=5000 auto-multicast=true sync=false

#Client
gst-launch-0.10 \
udpsrc auto-multicast=true multicast-group=224.1.1.1 port=5000 ! \
"audio/x-raw-int, endianness=(int)1234, signed=(boolean)true, width=(int)32, depth=(int)32, rate=(int)44100, channels=(int)2" ! \
gstrtpbin ! \
alsasink sync=false