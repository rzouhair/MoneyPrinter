import os
import random
import uuid
from venv import logger

from captions import add_captions
import requests
import srt_equalizer
import assemblyai as aai

from typing import List
from moviepy.editor import *
from termcolor import colored
from dotenv import load_dotenv
from datetime import timedelta
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

load_dotenv("../.env")

ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")

def save_video(video_url: str, directory: str = "../temp") -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    video_id = uuid.uuid4()
    video_path = f"{directory}/{video_id}.mp4"

    logger.info(f"Saving {video_url} to {video_path}")

    payload = {}
    headers = {
      'Authorization': 'ZW7nMLprvXyJub29QkWBYcfemuRxE9rUbtejdrLLm52snO2TbwQzED2k',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    video_url_response_2 = requests.request("GET", video_url, headers=headers, data=payload)

    logger.info(f"Saving video... {video_url_response_2.content}")
    with open(video_path, "wb") as f:
        f.write(video_url_response_2.content)

    return video_path

def save_image(video_url: str, directory: str = "../temp") -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    photo_id = uuid.uuid4()
    photo_path = f"{directory}/{photo_id}.png"

    payload = {}
    headers = {
      'Authorization': 'ZW7nMLprvXyJub29QkWBYcfemuRxE9rUbtejdrLLm52snO2TbwQzED2k',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    video_url_response_2 = requests.request("GET", video_url, headers=headers, data=payload)

    with open(photo_path, "wb") as f:
        f.write(video_url_response_2.content)

    return photo_path


def __generate_subtitles_assemblyai(audio_path: str, voice: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.

    Returns:
        str: The generated subtitles
    """

    language_mapping = {
        "br": "pt",
        "id": "en", #AssemblyAI doesn't have Indonesian 
        "jp": "ja",
        "kr": "ko",
    }

    if voice in language_mapping:
        lang_code = language_mapping[voice]
    else:
        lang_code = voice

    aai.settings.api_key = ASSEMBLY_AI_API_KEY
    config = aai.TranscriptionConfig(language_code=lang_code)
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)
    subtitles = transcript.export_subtitles_srt()

    return subtitles


def __generate_subtitles_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track
    Returns:
        str: The generated subtitles
    """

    def convert_to_srt_time_format(total_seconds):
        # Convert total seconds to the SRT time format: HH:MM:SS,mmm
        if total_seconds == 0:
            return "0:00:00,0"
        return str(timedelta(seconds=total_seconds)).rstrip('0').replace('.', ',')

    start_time = 0
    subtitles = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
        duration = audio_clip.duration
        end_time = start_time + duration

        # Format: subtitle index, start time --> end time, sentence
        subtitle_entry = f"{i}\n{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n{sentence}\n"
        subtitles.append(subtitle_entry)

        start_time += duration  # Update start time for the next subtitle

    return "\n".join(subtitles)


def generate_subtitles(audio_path: str, sentences: List[str], audio_clips: List[AudioFileClip], voice: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track

    Returns:
        str: The path to the generated subtitles.
    """

    def equalize_subtitles(srt_path: str, max_chars: int = 10) -> None:
        # Equalize subtitles
        srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)

    # Save subtitles
    subtitles_path = f"../subtitles/{uuid.uuid4()}.srt"

    if ASSEMBLY_AI_API_KEY is not None and ASSEMBLY_AI_API_KEY != "":
        print(colored("[+] Creating subtitles using AssemblyAI", "blue"))
        subtitles = __generate_subtitles_assemblyai(audio_path, voice)
    else:
        print(colored("[+] Creating subtitles locally", "blue"))
        subtitles = __generate_subtitles_locally(sentences, audio_clips)
        # print(colored("[-] Local subtitle generation has been disabled for the time being.", "red"))
        # print(colored("[-] Exiting.", "red"))
        # sys.exit(1)

    logger.info("========== SUBTITLES ==========")
    logger.info(subtitles)
    logger.info("========== SUBTITLES ==========")

    with open(subtitles_path, "w") as file:
        file.write(subtitles)

    # Equalize subtitles
    equalize_subtitles(subtitles_path)

    print(colored("[+] Subtitles generated.", "green"))

    return subtitles_path


def combine_videos(video_paths: List[str], max_duration: int, max_clip_duration: int, threads: int, target_resolution: tuple) -> str:
    """
    Combines a list of videos into one video and returns the path to the combined video.

    Args:
        video_paths (List): A list of paths to the videos to combine.
        max_duration (int): The maximum duration of the combined video.
        max_clip_duration (int): The maximum duration of each clip.
        threads (int): The number of threads to use for the video processing.

    Returns:
        str: The path to the combined video.
    """
    video_id = uuid.uuid4()
    combined_video_path = f"../temp/{video_id}.mp4"
    
    # Required duration of each clip
    req_dur = max_duration / len(video_paths)


    print(colored("[+] Combining videos...", "blue"))
    logger.info(colored("[+] Combining videos...", "blue"))
    print(colored(f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"))
    logger.info(colored(f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"))

    clips = []
    tot_dur = 0
    logger.info("Add downloaded clips over and over until the duration of the audio (max_duration) has been reached")
    # Add downloaded clips over and over until the duration of the audio (max_duration) has been reached
    while tot_dur < max_duration:
        for video_path in video_paths:
            clip = VideoFileClip(video_path)
            clip = clip.without_audio()
            logger.info("Check if clip is longer than the remaining audio")
            # Check if clip is longer than the remaining audio
            if (max_duration - tot_dur) < clip.duration:
                clip = clip.subclip(0, (max_duration - tot_dur))
            # Only shorten clips if the calculated clip length (req_dur) is shorter than the actual clip to prevent still image
            elif req_dur < clip.duration:
                clip = clip.subclip(0, req_dur)
            clip = clip.set_fps(30)

            logger.info("Not all videos are same size, so we need to resize them")
            # Not all videos are same size,
            # so we need to resize them
            if round((clip.w/clip.h), 4) < 0.5625:
                clip = crop(clip, width=clip.w, height=round(clip.w/0.5625), \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            else:
                clip = crop(clip, width=round(0.5625*clip.h), height=clip.h, \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            clip = clip.resize(target_resolution)

            if clip.duration > max_clip_duration:
                clip = clip.subclip(0, max_clip_duration)

            clips.append(clip)
            tot_dur += clip.duration

    final_clip = concatenate_videoclips(clips)
    final_clip = final_clip.set_fps(30)
    final_clip.write_videofile(combined_video_path, threads=threads)

    return combined_video_path

def text_with_shadow(txt, font="Montserrat-Black", fontsize=120, color="white", stroke_color="black", stroke_width=40, shadow_color="black", shadow_offset=(-5, 0), highlight_color="yellow"):
    text_clip = TextClip(
        txt,
        font=font,
        fontsize=fontsize,
        color=highlight_color if random.choice([1, 2, 3, 5, 6, 7]) == 1 else color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
    )

    shadow_clip = TextClip(
        txt,
        font=font,
        fontsize=fontsize,
        color=shadow_color,
    )
    
    result = CompositeVideoClip([shadow_clip, text_clip])

    return result.set_duration(text_clip.duration)

def generate_video(combined_video_path: str, tts_path: str, subtitles_path: str, threads: int, subtitles_position: str,  text_color : str) -> str:
    """
    This function creates the final video, with subtitles and audio.

    Args:
        combined_video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.
        threads (int): The number of threads to use for the video processing.
        subtitles_position (str): The position of the subtitles.

    Returns:
        str: The path to the final video.
    """

    def scaling_factor(t):
        scale_factor = 0.5 + 0.5 * t  # Scale linearly over time (from 1.0 to 1.5 over 1 second)
        return scale_factor
    # Make a generator that returns a TextClip when called with consecutive
    """ generator = lambda txt: text_with_shadow(
        txt,
        font="/Users/user/Library/Fonts/Poppins-Bold.ttf",
        fontsize=120,
        color=text_color,
        highlight_color="yellow",
        shadow_color="black",
        stroke_width=1,
        stroke_color="black",
        shadow_offset=(0, 0)
    ) """

    # Split the subtitles position into horizontal and vertical
    horizontal_subtitles_position, vertical_subtitles_position = subtitles_position.split(",")

    # Burn the subtitles into the video
   #  subtitles = SubtitlesClip(subtitles_path, generator)
    # Add the audio
    audio = AudioFileClip(tts_path)

    result = VideoFileClip(combined_video_path)

    """ result = CompositeVideoClip([
      VideoFileClip(combined_video_path),
      subtitles.set_pos((horizontal_subtitles_position, vertical_subtitles_position))
    ]) """

    result = result.set_audio(audio)

    logger.info("Writing Video")
    result.write_videofile("../temp/output.mp4", threads=threads or 2)
    logger.info("Video Written")

    logger.info("Adding captions")

    add_captions(
      video_file="../temp/output.mp4",
      output_file="../temp/my_short_with_captions.mp4",

      # get current project absolute path
      font=os.path.abspath(os.path.join(os.path.dirname(__file__), "captions/assets/fonts/Bangers-Regular.ttf")),
      font_size = 120,
      font_color = "white",

      stroke_width = 5,
      stroke_color = "black",

      shadow_strength = 0.0,
      shadow_blur = 0.0,

      highlight_current_word = True,
      word_highlight_color = "yellow",

      line_count=1,
      position=(horizontal_subtitles_position, vertical_subtitles_position),

      padding = 50,
      use_local_whisper=False
    )

    return "my_short_with_captions.mp4"


def generateImage (prompt, options = {
  "model": 'V_1_TURBO',
  "aspect_ratio": 'ASPECT_9_16',
  "magic_prompt_option": 'OFF'
}):
  url = "https://api.ideogram.ai/generate"

  apiKey = '-3ooLqGcCHOaZNB7r6hMwHOB1Enn82EDlRnAbp2nB-iqpKEtORy5R-4nngVzvgOHqStHssRgz_n0VrcFIlmjSg'

  payload = { "image_request": {
          "prompt": prompt,
          "aspect_ratio": options.get('aspect_ratio', 'ASPECT_16_9'),
          "model": options.get('model', 'V_2'),
          "magic_prompt_option": options.get('magic_prompt_option', 'OFF')
      } }
  headers = {
      "Api-Key": apiKey,
      "Content-Type": "application/json"
  }

  response = requests.post(url, json=payload, headers=headers)

  return response.json()