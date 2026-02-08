import time
import queue
import threading
import logging
import sounddevice as sd

logger = logging.getLogger(__name__)

audio_queue = queue.Queue(maxsize=5)
stop_event = threading.Event()
producer_thread = None
consumer_thread = None


def _clear_queue():
    try:
        while True:
            audio_queue.get_nowait()
    except queue.Empty:
        logger.debug("Audio queue is now empty")
        return

"""Generates audio but takes mandatory 'breathers' to cool the GPU."""
def audio_producer(generator, cool_down=2.0):
    logger.info("producer thread started: %s", threading.current_thread().name)
    for i, (gs, ps, audio) in enumerate(generator):
        if stop_event.is_set():
            break
        logger.debug("pushed item %s", i)
        try:
            audio_queue.put(audio, timeout=0.5)
        except queue.Full:
            logger.debug("Audio queue is full")
            if stop_event.is_set():
                break
            continue
        time.sleep(cool_down) 

    audio_queue.put(None)


""" Playback happens here.Since the AI is throttled, it might finish a chunk 
    just as you finish listening to the previous one."""
def _playback_consumer(sample_rate=24000):
    logger.info("listener thread started: %s", threading.current_thread().name)
    time.sleep(0.5)
    while True:
        try:
            chunk = audio_queue.get(timeout=0.5)
        except queue.Empty:
            logger.debug("Audio queue is empty")
            if stop_event.is_set():
                break
            continue
        logger.debug("pop item %s", audio_queue.qsize())
        if chunk is None:
            break
        if stop_event.is_set():
            break
        sd.play(chunk, sample_rate)
        sd.wait()


def start_playback_async(generator, sample_rate=24000, cool_down_time=1.5):
    global producer_thread
    global consumer_thread

    stop_event.clear()
    _clear_queue()

    producer_thread = threading.Thread(
        target=audio_producer,
        args=(generator, cool_down_time),
        daemon=True,
    )
    consumer_thread = threading.Thread(
        target=_playback_consumer,
        args=(sample_rate,),
        daemon=True,
    )
    producer_thread.start()
    consumer_thread.start()


def stop_playback():
    stop_event.set()
    try:
        sd.stop()
    except Exception as e:
        logger.error("Error stopping audio: %s", e)
    _clear_queue()
    try:
        audio_queue.put_nowait(None)
    except queue.Full:
        pass
   
