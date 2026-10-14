\# Real-Time Serial Packet Protocol \& Telemetry Station



A lightweight, robust binary serial communication protocol and host telemetry GUI designed for microcontroller-to-PC data acquisition.



Unlike traditional string-based streaming (`Serial.println`), this project implements a fixed-size byte-oriented packet structure with frame synchronization (`Header` / `Tail`) and bitwise reconstruction to maximize bandwidth and guarantee data integrity over noisy channels.



\---



\## 📌 Protocol Architecture



Packets are transmitted as fixed 5-byte binary frames at \*\*115200 baud\*\*:



```text

┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐

│    BYTE 0    │    BYTE 1    │    BYTE 2    │    BYTE 3    │    BYTE 4    │

├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤

│ 0xAA (Start) │ High Byte    │ Low Byte     │ Button State │  0x55 (End)  │

│ Frame Header │ Sensor (MSB) │ Sensor (LSB) │ (0x00 / 0x01)│  Frame Tail  │

└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

```



\- \*\*Header (`0xAA`) \& Tail (`0x55`):\*\* Act as synchronization delimiters to recover stream alignment even during physical cable disconnects or buffer corruption.

\- \*\*Payload:\*\* 

&#x20; - 10-bit Analog ADC reading split into 2 bytes via bitwise shift (`>> 8` and `\& 0xFF`).

&#x20; - 1-byte discrete digital input flag (push-button).



\---



\## 🚀 Features



\- \*\*Byte-Hunting State Machine:\*\* The host parser reads incoming serial streams byte-by-byte until `0xAA` is validated, preventing packet misalignment.

\- \*\*Hardware Agnostic:\*\* Features a built-in dummy stream generator for GUI testing when physical microcontrollers are unavailable.

\- \*\*Live Telemetry Interface:\*\* Real-time dynamic waveform rendering via `matplotlib` interactive mode, including visual event triggers (color warning on button press).



\---



\## 🛠️ Getting Started



\### Prerequisites

Install required Python dependencies:

```bash

pip install -r requirements.txt

```



\### Running the Host Telemetry

To run the live visualization dashboard:

```bash

python host/telemetry\_gui.py

```

