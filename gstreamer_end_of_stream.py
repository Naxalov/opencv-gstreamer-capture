import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import time

def on_new_sample(sink):
    """Callback triggered when a new sample is ready from appsink."""
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR

    # Get the buffer from the sample
    buf = sample.get_buffer()
    caps = sample.get_caps()

    # Map the buffer data (i.e., get the actual bytes of the frame)
    result, map_info = buf.map(Gst.MapFlags.READ)
    if not result:
        return Gst.FlowReturn.ERROR
    
    # Get the frame dimensions
    width = caps.get_structure(0).get_value("width")
    height = caps.get_structure(0).get_value("height")
    # format = caps.get_structure(0).get_string("format")
    print(f'Width: {width}, Height: {height})')

    try:
        frame_data = map_info.data
        # For simplicity, assume it's a raw RGB or BGR frame
        # The caps might give more detail if needed
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        print(frame.shape)
        
    

        # Now you can do something with 'frame' (e.g., process with OpenCV)
        # ...
    finally:
        buf.unmap(map_info)

    return Gst.FlowReturn.OK

def on_eos(bus, message,loop,start_time):
    """
    Called when EOS (End of Stream) message is posted on the bus.
    """
    end_time = time.time() - start_time
    print("Reached end of stream.")
    print(f'Execution time: {end_time:.3f} seconds')
    # loop.quit()
    

   

def main():
    Gst.init(None)

    pipeline_str = (
        "filesrc location=sample_720p.mp4 ! "
        "decodebin ! "
        "videoconvert ! "
        "video/x-raw, format=RGB ! "
        # For GStreamer 1.0, we typically have 'appsink'
        "appsink name=mysink emit-signals=true sync=false"
    )

    print('Starting pipeline execution')


    pipeline = Gst.parse_launch(pipeline_str)

    # Grab appsink element by name
    sink = pipeline.get_by_name("mysink")
    # Connect the callback for new samples
    sink.connect("new-sample", on_new_sample)

    # Start playing
    pipeline.set_state(Gst.State.PLAYING)

    # Start the timer
    start_time = time.time()

    # Watch the bus for EOS messages
    bus = pipeline.get_bus()
    bus.add_signal_watch()

    loop = GLib.MainLoop()

    bus.connect("message", on_eos, loop, start_time)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
