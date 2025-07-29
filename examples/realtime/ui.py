####################################################################
# Pure-python web app for speaking with the realtime voice api     #
# Data is relayed to/from server using WebRTC                      #
# You can run this example with just                               #
#                                                                  #
# `python ./examples/realtime/ui.py`                               #
####################################################################

from __future__ import annotations
import base64
import os
from threading import Event, Thread

import gradio as gr
import numpy as np
import openai
from dotenv import load_dotenv
from gradio_webrtc import (
    AdditionalOutputs,
    StreamHandler,
    WebRTC
)
from openai.types.beta.realtime import ResponseAudioTranscriptDoneEvent
from pydub import AudioSegment

load_dotenv()

SAMPLE_RATE = 24000


def encode_audio(sample_rate, data):
    segment = AudioSegment(
        data.tobytes(),
        frame_rate=sample_rate,
        sample_width=data.dtype.itemsize,
        channels=1,
    )
    pcm_audio = (
        segment.set_frame_rate(SAMPLE_RATE).set_channels(1).set_sample_width(2).raw_data
    )
    return base64.b64encode(pcm_audio).decode("utf-8")


class OpenAIHandler(StreamHandler):
    def __init__(
        self,
        expected_layout="mono",
        output_sample_rate=SAMPLE_RATE,
        output_frame_size=480,
    ) -> None:
        super().__init__(
            expected_layout,
            output_sample_rate,
            output_frame_size,
            input_sample_rate=SAMPLE_RATE,
        )
        self.connection = None
        self.all_output_data = None
        self.quit = Event()
        self.connected = Event()
        self.thread = None
        self._generator = None

    def copy(self):
        return OpenAIHandler(
            expected_layout=self.expected_layout,
            output_sample_rate=self.output_sample_rate,
            output_frame_size=self.output_frame_size,
        )

    def _initialize_connection(self, api_key: str):
        """Connect to realtime API. Run forever in separate thread to keep connection open."""
        self.client = openai.Client(api_key=api_key)
        with self.client.beta.realtime.connect(
            model="gpt-4o-mini-realtime-preview-2024-12-17"
        ) as conn:
            conn.session.update(session={"turn_detection": {"type": "server_vad"}})
            self.connection = conn
            self.connected.set()
            self.quit.wait()

    def receive(self, frame: tuple[int, np.ndarray]) -> None:
        if not self.connection:
            self.wait_for_args_sync()
            self.thread = Thread(
                target=self._initialize_connection, args=(self.latest_args[-1],)
            )
            self.thread.start()
            self.connected.wait()
        try:
            assert self.connection, "Connection not initialized"
            sample_rate, array = frame
            array = array.squeeze()
            audio_message = encode_audio(sample_rate, array)
            self.connection.input_audio_buffer.append(audio=audio_message)
        except Exception as e:
            # print traceback
            print(f"Error in receive: {str(e)}")
            import traceback

            traceback.print_exc()

    def generator(self):
        while True:
            if not self.connection:
                yield None
                continue
            for event in self.connection:
                if event.type == "response.audio_transcript.done":
                    yield AdditionalOutputs(event)
                if event.type == "response.audio.delta":
                    yield (
                        self.output_sample_rate,
                        np.frombuffer(
                            base64.b64decode(event.delta), dtype=np.int16
                        ).reshape(1, -1),
                    )

    def emit(self) -> tuple[int, np.ndarray] | None:
        if not self.connection:
            return None
        if not self._generator:
            self._generator = self.generator()
        try:
            return next(self._generator)
        except StopIteration:
            self._generator = self.generator()
            return None
    
    def reset_state(self):
        """Reset connection state for new recording session"""
        self.connection = None
        self.quit.clear()
        self.connected.clear()
        self.thread = None
        self._generator = None

    def shutdown(self) -> None:
        if self.connection:
            self.connection.close()
            self.quit.set()
            if self.thread:
                self.thread.join(timeout=5)
            self.reset_state()


def update_chatbot(chatbot: list[dict], response: ResponseAudioTranscriptDoneEvent):
    chatbot.append({"role": "assistant", "content": response.transcript})
    return chatbot


with gr.Blocks() as demo:
    gr.HTML("""
    <div style='display: flex; align-items: center; justify-content: center; gap: 20px'>
        <div style="background-color: var(--block-background-fill); border-radius: 8px">
            <img src="https://huggingface.co/datasets/freddyaboulton/bucket/resolve/main/openai-logo.svg" style="width: 100px; height: 100px;">
        </div>
        <div>
            <h1>OpenAI Realtime Voice Chat</h1>
            <p>Speak with OpenAI's latest using real-time audio streaming api.</p>
            <p>Powered by <a href="https://gradio.app/">Gradio</a> and <a href==https://freddyaboulton.github.io/gradio-webrtc/">WebRTC</a>⚡️</p>
            <p>Get an API key from <a href="https://platform.openai.com/">OpenAI</a>.</p>
        </div>
    </div>
    """)

    with gr.Row(visible=True) as api_key_row:
        api_key = gr.Textbox(
            label="OpenAI API Key",
            placeholder="Enter your OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
        )
    with gr.Row(visible=False) as row:
        with gr.Column(scale=1):
            webrtc = WebRTC(
                label="Conversation",
                modality="audio",
                mode="send-receive",
                icon="https://huggingface.co/datasets/freddyaboulton/bucket/resolve/main/openai-logo.svg",
            )
        with gr.Column(scale=5):
            chatbot = gr.Chatbot(label="Conversation", value=[], type="messages")
        webrtc.stream(
            OpenAIHandler(),
            inputs=[webrtc, api_key],
            outputs=[webrtc],
            time_limit=90,
            concurrency_limit=2,
        )
        webrtc.on_additional_outputs(
            update_chatbot,
            inputs=[chatbot],
            outputs=[chatbot],
            show_progress="hidden",
            queue=True,
        )
    api_key.submit(
        lambda: (gr.update(visible=False), gr.update(visible=True)),
        None,
        [api_key_row, row],
    )


if __name__ == "__main__":
    demo.launch()