import time

import cv2
import obsws_python as obs

import config


def has_line(data, x1, y1, x2, y2, r, g, b):
    for y in range(y1, y2):
        for x in range(x1, x2):
            pixel = data[y, x]

            cr = pixel[2]
            cg = pixel[1]
            cb = pixel[0]

            if not (r - 40 < cr < r + 40 and g - 40 < cg < g + 40 and b - 40 < cb < b + 40):
                return False

    return True


def is_gameplay(data, yoffset):
    return \
            (has_line(data, 494, 11 + yoffset, 495, 11 + yoffset + 51, 255, 255, 255) or
             has_line(data, 1425, 11 + yoffset, 1426, 11 + yoffset + 51, 255, 255, 255)) and \
            has_line(data, 580, 43 + yoffset, 1400, 43 + yoffset, 0, 0, 0)


def main():
    client = obs.ReqClient(host='localhost', port=4455, password=config.OBS_PASSWORD, timeout=3)
    client.set_source_filter_settings(config.PLAYER1_VIDEO_SOURCE, 'Dynamic Delay', {'duration': 0}, True)
    client.set_source_filter_settings(config.PLAYER2_VIDEO_SOURCE, 'Dynamic Delay', {'duration': 0}, True)

    client.set_input_mute(config.PLAYER1_AUDIO_SOURCE, True)
    client.set_input_mute(config.PLAYER2_AUDIO_SOURCE, True)

    cap = cv2.VideoCapture(config.WEBCAM)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    p1frame = None
    p2frame = None
    synced = False

    frame = 1

    while cap.isOpened():
        res, image = cap.read()

        if config.DEBUG:
            cv2.imshow('Preview', image)
            cv2.waitKey(1)

        p1gameplay = is_gameplay(image, 0)
        p2gameplay = is_gameplay(image, int(1080 / 2))

        if p1gameplay:
            if not p1frame:
                p1frame = frame
                print(f"p1frame in: {frame}")
        elif p1frame:
            synced = False
            p1frame = None
            client.set_input_mute(config.PLAYER1_AUDIO_SOURCE, True)
            client.set_source_filter_settings(config.PLAYER1_VIDEO_SOURCE, 'Dynamic Delay', {'duration': 0}, True)
            print(f"p1frame out: {frame}")

        if p2gameplay:
            if not p2frame:
                p2frame = frame
                print(f"p2frame in: {frame}")
        elif p2frame:
            synced = False
            p2frame = None
            client.set_input_mute(config.PLAYER2_AUDIO_SOURCE, True)
            client.set_source_filter_settings(config.PLAYER2_VIDEO_SOURCE, 'Dynamic Delay', {'duration': 0}, True)
            print(f"p2frame out: {frame}")

        if not synced and p1frame and p2frame:
            synced = True

            delay = abs(p1frame - p2frame) * 16.67 / 1000

            if p1frame < p2frame and delay <= 10:
                print(f"Delay p1 by {delay:.2f}s")

                client.set_source_filter_settings(config.PLAYER1_VIDEO_SOURCE, 'Dynamic Delay', {'duration': delay}, True)

                client.set_input_mute(config.PLAYER1_AUDIO_SOURCE, True)
                client.set_input_mute(config.PLAYER2_AUDIO_SOURCE, False)

                time.sleep(0.1)
                client.trigger_hotkey_by_key_sequence('OBS_KEY_F6', False, False, False, False)
            elif p2frame < p1frame and delay <= 10:
                print(f"Delay p2 by {delay:.2f}s")
                client.set_source_filter_settings(config.PLAYER2_VIDEO_SOURCE, 'Dynamic Delay', {'duration': delay}, True)

                client.set_input_mute(config.PLAYER1_AUDIO_SOURCE, False)
                client.set_input_mute(config.PLAYER2_AUDIO_SOURCE, True)

                time.sleep(0.1)
                client.trigger_hotkey_by_key_sequence('OBS_KEY_F8', False, False, False, False)
            else:
                # Use p1 audio if the streams are already synced
                client.set_input_mute(config.PLAYER1_AUDIO_SOURCE, False)

        frame += 1


if __name__ == '__main__':
    main()
