import time
import pymiere
from pymiere import wrappers
import math


SECONDS_BETWEEN_AUDIOCLIPS = 1.3

def add_seconds_btwn_audio(sequence, fps):
    """
    adding seconds between every audio clip and 
    return the list of their start, end frame points
    """
    audio_clips = sequence.audioTracks[0].clips

    last_frame = fps * audio_clips[0].end.seconds
    first_clip = audio_clips[0]

    frames_for_sub = list()
    frames_for_sub.append(
        (first_clip.start.seconds * fps, first_clip.end.seconds * fps)
        )

    for aclip in audio_clips:

        if not aclip.name == first_clip.name:

            start = last_frame
            end = start + (fps * aclip.duration.seconds)

            in_point = 0
            out_point = end - start

            # end - start has to equal out_point - in_point
            wrappers.edit_clip(aclip, start, end, in_point, out_point, fps=fps)

            # set the frame to continue the next clip from
            last_frame = end + fps * SECONDS_BETWEEN_AUDIOCLIPS
            frames_for_sub.append((start, end))

    return frames_for_sub


def align_video_clips_to_audio(frames_for_sub):
    """
    adjust video clips to the dubbing audio
    """
    video_clips = sequence.videoTracks[0].clips

    for idx, vclip in enumerate(video_clips):

        start = frames_for_sub[idx][0]

        if idx != len(frames_for_sub) - 1:
            end = frames_for_sub[idx+1][0]
        else: # reached the last tuple
            end = frames_for_sub[idx][1]

        in_point = 0
        out_point = end - start

        wrappers.edit_clip(vclip, start, end, in_point, out_point)

if __name__ == '__main__':

    project = pymiere.objects.app.project
    sequence = project.activeSequence

    fps = 1/(float(project.activeSequence.timebase)/wrappers.TICKS_PER_SECONDS)

    frames_for_sub = add_seconds_btwn_audio(sequence, fps)
    align_video_clips_to_audio(frames_for_sub)