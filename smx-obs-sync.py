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
    video_sources = config.PLAYER1_VIDEO_SOURCES + config.PLAYER2_VIDEO_SOURCES
    audio_sources = config.PLAYER1_AUDIO_SOURCES + config.PLAYER2_AUDIO_SOURCES
    shortcuts = ['OBS_KEY_F6', 'OBS_KEY_F8']

    client = obs.ReqClient(host='localhost', port=4455, password=config.OBS_PASSWORD, timeout=3)

    for source in video_sources:
        client.set_source_filter_settings(source, 'Dynamic Delay', {'duration': 0}, True)

    cap = cv2.VideoCapture(config.WEBCAM)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    gameplay_frame = [None, None]
    synced = False

    frame = 0

    while cap.isOpened():
        res, image = cap.read()
        frame += 1

        if config.DEBUG:
            cv2.imshow('Preview', image)
            cv2.waitKey(1)

        gameplay = [is_gameplay(image, 0), is_gameplay(image, int(1080 / 2))]

        for i in [0, 1]:
            if gameplay[i] and not gameplay_frame[i]:
                print(f'Player {i + 1} first gameplay frame: {frame}')
                gameplay_frame[i] = frame

                for source in audio_sources:
                    client.set_input_mute(source, False)

            if not gameplay[i] and gameplay_frame[i]:
                print(f'Player {i + 1} last gameplay frame: {frame}')
                gameplay_frame[i] = None

                for source in video_sources:
                    client.set_source_filter_settings(source, 'Dynamic Delay', {'duration': 0}, True)

                for source in audio_sources:
                    client.set_input_mute(source, False)

                synced = False

        if not synced and all(gameplay_frame):
            synced = True

            delay = abs(gameplay_frame[0] - gameplay_frame[1]) * 16.67 / 1000

            if delay == 0 or delay > 10:
                continue

            delayed_player = 0 if gameplay_frame[0] < gameplay_frame[1] else 1
            print(f'Player {delayed_player + 1} delayed by: {delay:.2f}s')

            for source in [config.PLAYER1_VIDEO_SOURCES, config.PLAYER2_VIDEO_SOURCES][delayed_player]:
                client.set_source_filter_settings(source, 'Dynamic Delay', {'duration': delay}, True)

            for source in [config.PLAYER1_AUDIO_SOURCES, config.PLAYER2_AUDIO_SOURCES][delayed_player]:
                client.set_input_mute(source, True)

            for source in [config.PLAYER2_AUDIO_SOURCES, config.PLAYER1_AUDIO_SOURCES][delayed_player]:
                client.set_input_mute(source, False)

            time.sleep(0.1)
            client.trigger_hotkey_by_key_sequence(shortcuts[delayed_player], False, False, False, False)


if __name__ == '__main__':
    main()
