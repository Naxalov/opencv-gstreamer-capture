import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

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
        "videotestsrc num-buffers=300000 ! "
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
