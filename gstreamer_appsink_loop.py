import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import cv2 
import numpy as np

def main():
    """
    Initialize GStreamer and set up the pipeline.
    """
    Gst.init(None)

    # ----------------------- 
    # Build the GStreamer pipeline
    # -----------------------
    # This pipeline uses a test source
    # The pipeline:
    # videotestsrc -> videoconvert -> video/x-raw, format=RGB -> appsink
    pipeline_str = (
        "videotestsrc num-buffers=300 ! "
        "videoconvert ! "
        "video/x-raw, format=RGB ! "
        "appsink name=mysink max-buffers=1 drop=true"
    )

    print('Starting pipeline execution')
    pipeline = Gst.parse_launch(pipeline_str)

    # Get the appsink element by name
    sink = pipeline.get_by_name("mysink")
    
    # Set the pipeline to play
    pipeline.set_state(Gst.State.PLAYING)

    
    try:
        while True:
            # Wait for the next sample
            sample = sink.emit("pull-sample")
            if not sample:
                break

            # Get the buffer from the sample (i.e., get the actual bytes of the frame)
            buf = sample.get_buffer()
            # Get the caps from the sample (i.e., get the frame dimensions)
            caps = sample.get_caps()

            # Map the buffer data (i.e., get the actual bytes of the frame)
            result, map_info = buf.map(Gst.MapFlags.READ)
            if not result:
                continue
            # Get the frame dimensions
            width = caps.get_structure(0).get_value("width")
            height = caps.get_structure(0).get_value("height")
            print(f'Width: {width}, Height: {height})')

            # Convert the buffer data to a NumPy array
            frame_data = map_info.data
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape(height, width, 3)

            # Display the frame using OpenCV
            cv2.imshow("Frame", frame)

            # Wait for a key press
            key = cv2.waitKey(1)
            

            

            # Unmap the buffer
            buf.unmap(map_info)
            # Release the buffer
            buf = None

    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        # Stop the pipeline
        pipeline.set_state(Gst.State.NULL) 
        # Close any OpenCV windows
        cv2.destroyAllWindows() 



if __name__ == "__main__":
    main()