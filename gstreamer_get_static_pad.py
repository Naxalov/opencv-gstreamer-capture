import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
def bus_call(bus, message, loop):
    msg_type = message.type
    if msg_type == Gst.MessageType.EOS:
        print("End-of-stream received. Quitting main loop.")
        loop.quit()
    elif msg_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Error: {}: {}".format(err, debug))
        loop.quit()
    return True


def buffer_probe(pad, info,user_data):
    """
    Probe function to access buffers before writing to filesink.
    """
    buffer = info.get_buffer()
    # Map the buffer data (i.e., get the actual bytes of the frame)
    result, map_info = buffer.map(Gst.MapFlags.READ)
    if not result:
        return Gst.PadProbeReturn.ERROR
    
    # Retrive the current caps from the pad to get the frame dimensions
    caps = pad.get_current_caps()
    width = caps.get_structure(0).get_value("width")
    height = caps.get_structure(0).get_value("height")
    print(f'Width: {width}, Height: {height})')

    # Convert the buffer data to a NumPy array
    frame_data = map_info.data
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    
    
    return Gst.PadProbeReturn.OK


def main():
    """
    Initialize GStreamer, set up the pipeline, and run until EOS is reached.
    """
    Gst.init(None)

    # ----------------------- 
    # Build the GStreamer pipeline
    # -----------------------
    # This pipeline uses a test source:
    # videotestsrc -> videoconvert -> video/x-raw, format=RGB -> filesink
    # It will generate 30 buffers because of num-buffers=30.
    pipeline_str = (
        "videotestsrc num-buffers=300 ! "
        "videoconvert ! "
        "x264enc !"
        "mp4mux ! "
        
        "filesink location=output.mp4"
    )
    
    print('Starting pipeline execution')
    pipeline = Gst.parse_launch(pipeline_str)

    # Create a GLib MainLoop to run the pipeline.
    loop = GLib.MainLoop()

    # Get the pipeline's bus and set up a bus watch to listen for EOS or ERROR messages.
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # Get the videoconvert element by default name
    sink = pipeline.get_by_name("videoconvert0")
    # Get the pad of the filesink
    file_pad = sink.get_static_pad("sink")
    # add a probe to the pad
    file_pad.add_probe(Gst.PadProbeType.BUFFER, buffer_probe, None)

    # Start playing the pipeline.
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Keyboard Interrupt received, stopping pipeline...")
        loop.quit()
    finally:
        pipeline.set_state(Gst.State.NULL)
        loop.quit()
        print('Pipeline execution complete')

if __name__ == "__main__":
    main()
