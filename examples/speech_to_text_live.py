#!/usr/bin/env -S rye run python
import asyncio
import base64
import json
import os
import ssl
import threading
import queue
import numpy as np
import sounddevice as sd
import websockets
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

load_dotenv()
# Make sure that you have the api in the env.
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("OPENAI_API_KEY environment variable not set. Please set it.")
    API_KEY = input("Please enter your OpenAI API key: ")
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")

SAMPLE_RATE = 16000  # 16kHz sample rate
CHANNELS = 1 

websocket = None
is_recording = False
audio_stream = None
audio_queue = queue.Queue()
main_loop = None

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class InputAudioTranscription(BaseModel):
    model: str = "gpt-4o-mini-transcribe"
    prompt: str = ""
    language: str = "en"

class TurnDetection(BaseModel):
    type: Literal["server_vad"] = "server_vad"
    threshold: float = 0.5
    prefix_padding_ms: int = 300
    silence_duration_ms: int = 300

class InputAudioNoiseReduction(BaseModel):
    type: Literal["near_field"] = "near_field"

class SessionConfig(BaseModel):
    input_audio_format: Literal["pcm16"] = "pcm16"
    input_audio_transcription: InputAudioTranscription
    turn_detection: TurnDetection
    input_audio_noise_reduction: InputAudioNoiseReduction
    include: List[str] = Field(default_factory=lambda: ["item.input_audio_transcription.logprobs"])

class TranscriptionConfig(BaseModel):
    type: Literal["transcription_session.update"] = "transcription_session.update"
    session: SessionConfig

async def connect_to_openai():
    global websocket
    
    print("Connecting to OpenAI STT API...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    try:
        websocket = await websockets.connect(
            "wss://api.openai.com/v1/realtime?intent=transcription",
            extra_headers=headers,
            ssl=ssl_context
        )
        print("Connected to OpenAI Realtime API")
        
        transcription_model = model if model else "gpt-4o-mini-transcribe"
        
        input_audio_transcription = InputAudioTranscription(model=transcription_model)
        turn_detection = TurnDetection()
        input_audio_noise_reduction = InputAudioNoiseReduction()
        
        session_config = SessionConfig(
            input_audio_transcription=input_audio_transcription,
            turn_detection=turn_detection,
            input_audio_noise_reduction=input_audio_noise_reduction
        )
        
        config = TranscriptionConfig(session=session_config)
        
        await websocket.send(json.dumps(config.model_dump()))
        print("Transcription session configured")
        return True
        
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False

async def handle_event(event):
    event_type = event.get("type")
    
    if event_type == "error":
        error_msg = event.get('error', {}).get('message', 'Unknown error')
        # print(f"ERROR: {error_msg}") # commented out to not populate the console with redundanterrors
        pass
    
    elif event_type == "input_audio_buffer.speech_started":
        print("Speech detected - listening...")
    
    elif event_type == "input_audio_buffer.speech_stopped":
        print("Speech ended - processing...")
    
    elif event_type == "conversation.item.input_audio_transcription.completed":
        transcript = event.get("transcript", {})
        print(f"TRANSCRIPTION COMPLETED: {transcript}")
    
    # Uncomment if you want to see the conversation items created
    # elif event_type == "input_audio_buffer.committed":
    #     item_id = event.get('item_id')
    #     print(f"Audio buffer committed: {item_id}")
    # elif event_type == "conversation.item.created":
    #     item_id = event.get('item', {}).get('id')
    #     print(f"Conversation item created: {item_id}")

    

async def receive_events():
    global websocket
    
    if not websocket:
        print("WebSocket connection not established")
        return
    
    try:
        async for message in websocket:
            event = json.loads(message)
            await handle_event(event)
    except websockets.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def send_audio_to_api(audio_data):
    global websocket, is_recording
    
    if not websocket or not is_recording:
        return
    
    try:        
        base64_data = base64.b64encode(audio_data).decode('utf-8')
        
        # send audio data to the API
        await websocket.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": base64_data
        }))

    except Exception as e:
        print(f"Error sending audio to API: {e}")

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio callback status: {status}")
    
    audio_data = (indata * 32767).astype(np.int16).tobytes()
    
    audio_queue.put(audio_data)

def start_microphone():
    global is_recording, audio_stream
    
    if is_recording:
        print("Microphone is already recording")
        return
    
    try:
        blocksize = int(SAMPLE_RATE * 0.05)
        
        audio_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=audio_callback,
            blocksize=blocksize,
            dtype='float32'
        )
        audio_stream.start()
        
        is_recording = True
        print("Microphone recording started. Speak now...")
        print("Press Ctrl+C to stop recording.")
        
    except Exception as e:
        print(f"Error starting microphone: {e}")

def stop_microphone():
    global is_recording, audio_stream
    
    if not is_recording:
        return
        
    is_recording = False
    
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
        audio_stream = None
    
    print("Microphone recording stopped.")

async def close_connection():
    global websocket
    
    if is_recording:
        stop_microphone()
    
    if websocket:
        await websocket.close()
        print("WebSocket connection closed")
        websocket = None

async def process_audio_queue():
    global audio_queue
    
    while is_recording:
        try:
            audio_data = audio_queue.get(block=False)
            await send_audio_to_api(audio_data)
        except queue.Empty:
            await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Error processing audio queue: {e}")

async def main():
    global main_loop
    
    main_loop = asyncio.get_running_loop()
    
    if not await connect_to_openai():
        return
    
    receive_task = asyncio.create_task(receive_events())
    
    start_microphone()
    
    audio_process_task = asyncio.create_task(process_audio_queue())
    
    try:
        # Keep the main thread running until interrupted
        while True:
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    except Exception as e:
        # print(f"\nERROR: {e}")
        pass
    finally:
        # clean up
        if receive_task:
            receive_task.cancel()
        if audio_process_task:
            audio_process_task.cancel()
        await close_connection()
        print("Transcription service stopped.")

if __name__ == "__main__":
    asyncio.run(main())
