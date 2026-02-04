import time
import queue
import soundfile as sf
import numpy as np
import threading
import sounddevice as sd

audio_queue = queue.Queue(maxsize=5)

"""Generates audio but takes mandatory 'breathers' to cool the GPU."""
def audio_producer(generator, cool_down=2.0):
    print(f"producer thead ... {threading.current_thread().name}")
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"pushed item {i}")
        audio_queue.put(audio)
        time.sleep(cool_down) 
    
    audio_queue.put(None)


""" Playback happens here.Since the AI is throttled, it might finish a chunk 
    just as you finish listening to the previous one."""
def start_listening_cool(generator, sample_rate=24000, cool_down_time=1.5):
    # Pass the cooling time to the producer
    producer_thread = threading.Thread(
        target=audio_producer, 
        args=(generator, cool_down_time)
    )
    producer_thread.start()


    print(f"linstner thread: {threading.current_thread().name}")
    #all_audio = []
    print("starting playback")
    time.sleep(10)
    while True:
        chunk = audio_queue.get()
        print(f"pop item {audio_queue.qsize()}")
        if chunk is None:
            break
        sd.play(chunk, sample_rate)
        #all_audio.append(chunk)
        sd.wait() 
        
    print("--- Finished ---")
   
