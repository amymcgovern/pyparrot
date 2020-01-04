from pyparrot.Anafi import Anafi
from pyparrot.DroneVisionGUI import DroneVisionGUI
from pyparrot.Model import Model
import cv2


WRITE_IMAGES = False


class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()
        if img is not None and WRITE_IMAGES:
            cv2.imwrite(f"test_image_{self.index:06d}", img)
            self.index += 1


def demo_anafi_user_vision(anafi_vision, args):
    """
    Demo the user code to run with the run button for a mambo

    :param args:
    :return:
    """
    anafi = args[0]

    print("Sleeping for 15 seconds, move Anafi around to test vision")
    anafi.smart_sleep(15)

    print("Closing video stream")
    anafi.close_video()

    anafi.smart_sleep(5)

    print("Disconnecting Anafi")
    anafi.disconnect()


if __name__ == "__main__":
    anafi = Anafi()
    print("Connecting to Anafi...")

    if anafi.connect(num_retries=3):
        print("Connected to Anafi")

        # Update state info
        anafi.smart_sleep(1)
        anafi.ask_for_state_update()
        anafi.smart_sleep(1)

        print("Preparing to open video stream")
        anafi_vision = DroneVisionGUI(
            anafi,
            Model.ANAFI,
            buffer_size=200,
            user_code_to_run=demo_anafi_user_vision,
            user_args=(anafi,),
        )
        user_vision = UserVision(anafi_vision)
        anafi_vision.set_user_callback_function(
            user_vision.save_pictures, user_callback_args=None
        )

        print("Opening video stream")
        anafi_vision.open_video()
