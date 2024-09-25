
import uuid
import requests
import openai
import os


def save_image_locally(image_url):
    image_id = uuid.uuid4()
    image_path = f"{image_id}.jpeg"

    payload = {}
    headers = {
      'Authorization': 'ZW7nMLprvXyJub29QkWBYcfemuRxE9rUbtejdrLLm52snO2TbwQzED2k',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    response = requests.request("GET", image_url, headers=headers, data=payload)

    with open(image_path, "wb") as f:
        f.write(response.content)

    return image_path

# Implement openai TTS function
def openai_tts(text, voice):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(f"Converting text to speech...: {text}")
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    return response


def generateVideo():
    try:
        # Set global variable
        global GENERATING
        GENERATING = True

        # Clean
        clean_dir("../temp/")
        clean_dir("../subtitles/")


        # Parse JSON
        data = request.get_json()
        ai_model = data.get('aiModel', 'gpt-4o-mini')  # Get the AI model selected by the user
        n_threads = data.get('threads', 2)  # Amount of threads to use for video generation
        subtitles_position = data.get('subtitlesPosition')  # Position of the subtitles in the video
        text_color = data.get('color') # Color of subtitle text
        use_stock_videos = data.get('useStockVideos', False)

        video_script = data.get('videoScript', None)
        video_images = data.get('videoImages', None)

        target_resolution = data.get('targetResolution', '1920:1080').split(':')

        # Get 'useMusic' from the request data and default to False if not provided
        use_music = data.get('useMusic', False)

        # Get 'automateYoutubeUpload' from the request data and default to False if not provided
        automate_youtube_upload = data.get('automateYoutubeUpload', False)

        # Download songs
        if use_music:
            # Downloads a ZIP file containing popular TikTok Songs
            if songs_zip_url:
                fetch_songs(songs_zip_url)
            else:
                # Default to a ZIP file containing popular TikTok Songs
                fetch_songs("https://filebin.net/2avx134kdibc4c3q/drive-download-20240209T180019Z-001.zip")

        # Print little information about the video which is to be generated
        print_fn(colored("[Video to be generated]", "blue"))
        print_fn(colored("   AI Model: " + ai_model, "blue"))  # Print the AI model being used
        print_fn(colored("   Custom Prompt: " + data.get("customPrompt", ''), "blue"))  # Print the AI model being used



        if not GENERATING:
            return jsonify(
                {
                    "status": "error",
                    "message": "Video generation was cancelled.",
                    "data": [],
                }
            )
        
        voice = data["voice"]
        voice_prefix = voice[:2]

        if not voice:
            print_fn(colored("[!] No voice was selected. Defaulting to \"en_us_001\"", "yellow"))
            voice = "en_us_001"
            voice_prefix = voice[:2]


        # Generate a script
        print_fn(colored("[+] Generating script...", "blue"))
        script = video_script
        print_fn(colored("[+] Generated script", "blue"))
        print_fn(script)

        if use_stock_videos:
          print_fn(colored("[+] Searching for stock videos...", "blue"))
          print_fn(data['videoSubject'])
          print_fn(AMOUNT_OF_STOCK_VIDEOS)
          print_fn(script)
          print_fn(ai_model)
          # Generate search terms
          search_terms = get_search_terms(
              data["videoSubject"], AMOUNT_OF_STOCK_VIDEOS, script, ai_model
          )

          print_fn(colored("[+] Found search terms " + str(len(search_terms)), "blue"))
          print_fn(search_terms)
          print_fn(colored("[+] Found search terms " + str(len(search_terms)), "blue"))

          # Search for a video of the given search term
          video_urls = []

          # Defines how many results it should query and search through
          it = 15

          # Defines the minimum duration of each clip
          min_dur = 10

          # Loop through all search terms,
          # and search for a video of the given search term
          for search_term in search_terms:
              if not GENERATING:
                  return jsonify(
                      {
                          "status": "error",
                          "message": "Video generation was cancelled.",
                          "data": [],
                      }
                  )

              print_fn("Searching for stock videos...")
              print_fn(search_term)
              print_fn(os.getenv("PEXELS_API_KEY"))
              print_fn(it)
              print_fn(min_dur)
              found_urls = search_for_stock_videos(
                  search_term, os.getenv("PEXELS_API_KEY"), it, min_dur
              )

              print_fn(colored(f"\t=> \"{search_term}\" found {len(found_urls)} Videos", "cyan"))
              # Check for duplicates
              for url in found_urls:
                  if url not in video_urls:
                      video_urls.append(url)
                      break

          # Check if video_urls is empty
          if not video_urls:
              print_fn(colored("[-] No videos found to download.", "red"))
              return jsonify(
                  {
                      "status": "error",
                      "message": "No videos found to download.",
                      "data": [],
                  }
              )
              
          # Define video_paths
          video_paths = []

          # Let user know
          print_fn(colored(f"[+] Downloading {len(video_urls)} videos...", "blue"))

          # Save the videos
          for video_url in video_urls:
              if not GENERATING:
                  return jsonify(
                      {
                          "status": "error",
                          "message": "Video generation was cancelled.",
                          "data": [],
                      }
                  )
              try:
                  print_fn(f"Downloading {video_url}")
                  saved_video_path = save_video(video_url)
                  video_paths.append(saved_video_path)
              except Exception:
                  print_fn(colored(f"[-] Could not download video: {video_url}", "red"))

          # Let user know
          print_fn(colored("[+] Videos downloaded!", "green"))
        else:
            video_paths = []
            images_paths = []

            it = len(video_images) if video_images else 5
            # Let user know
            print_fn(colored(f"[+] Downloading {len(video_images)} images...", "blue"))

            # Save the videos
            for image_url in video_images:
                if not GENERATING:
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Video generation was cancelled.",
                            "data": [],
                        }
                    )
                try:
                    print_fn(f"Downloading {image_url}")
                    saved_image_path = save_image(image_url)
                    images_paths.append(saved_image_path)
                except Exception:
                    print_fn(colored(f"[-] Could not download video: {image_url}", "red"))

            # Let user know
            print_fn(colored("[+] Images downloaded!", "green"))

            print_fn("========== STOCK IMAGES ==========")
            print_fn(images_paths)
            print_fn("========== STOCK IMAGES ==========")

            img = images_paths if images_paths and len(images_paths) > 0 else ['./backend/img1.jpg', './backend/img2.jpg', './backend/img3.jpg']

            clips = [ImageClip(img[mi]).set_duration(script[mi]['duration'])
                  for mi in range(len(img))]

            for clip in clips:
              width, height = clip.size
              target_width = int(target_resolution[0])
              target_height = int(target_resolution[1])

              print_fn(f"Target Resolution: {target_width}x{target_height}")
              print_fn(f"Clip Resolution: {width}x{height}")
              if width < target_width:
                border_width = (target_width - width) // 2
                """ black_border_clip = ImageClip(Image.new("RGB", (border_width, tagert_height), (0, 0, 0)))
                composite_image_clip = CompositeVideoClip([black_border_clip, clip, black_border_clip])
                clip = composite_image_clip.set_duration(clip.duration)
                clip.margin(left=border_width, right=border_width, top=0, bottom=0) """

            concat_clip = concatenate_videoclips(clips, method="compose")
            concat_clip.write_videofile("../temp/test.mp4", fps=60)

            video_paths.append("../temp/test.mp4")
        # Let user know
        print_fn(colored("[+] Script generated!\n", "green"))

        if not GENERATING:
            return jsonify(
                {
                    "status": "error",
                    "message": "Video generation was cancelled.",
                    "data": [],
                }
            )

        # Split script into sentences
        # concat_script = '. '.join(s['dialogue'] for s in script)

        sentences = map(lambda s: s['dialogue'], script)

        # Remove empty strings
        # sentences = list(filter(lambda x: x != "", sentences))
        paths = []

        # Generate TTS for every sentence
        for sentence in sentences:
            if not GENERATING:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled.",
                        "data": [],
                    }
                )
            current_tts_path = f"../temp/{uuid4()}.mp3"
            tts(sentence, voice, filename=current_tts_path)
            audio_clip = AudioFileClip(current_tts_path)
            paths.append(audio_clip)

        # Combine all TTS files using moviepy
        final_audio = concatenate_audioclips(paths)
        tts_path = f"../temp/{uuid4()}.mp3"
        final_audio.write_audiofile(tts_path)

        try:
            subtitles_path = generate_subtitles(audio_path=tts_path, sentences=sentences, audio_clips=paths, voice=voice_prefix)
        except Exception as e:
            print_fn(colored(f"[-] Error generating subtitles: {e}", "red"))
            subtitles_path = None

        print_fn("Concatenate Videos")
        # Concatenate videos
        temp_audio = AudioFileClip(tts_path)
        print_fn("Temporary audio")
        combined_video_path = combine_videos(video_paths, temp_audio.duration, 5, n_threads or 2, target_resolution=(target_width, target_height))

        print_fn("Put everything together")
        # Put everything together
        try:
            final_video_path = generate_video(combined_video_path, tts_path, subtitles_path, n_threads or 2, subtitles_position, text_color or "#FFFFFF")
        except Exception as e:
            print_fn(colored(f"[-] Error generating final video: {e}", "red"))
            final_video_path = None

        try:
          # Define metadata for the video, we will display this to the user, and use it for the YouTube upload
          print_fn("Define metadata for the video, we will display this to the user, and use it for the YouTube upload")
          title, description, keywords = generate_metadata(data["videoSubject"], script, ai_model)
          print_fn(colored("[-] Metadata for YouTube upload:", "blue"))
          print_fn(colored("   Title: ", "blue"))
          print_fn(colored(f"   {title}", "blue"))
          print_fn(colored("   Description: ", "blue"))
          print_fn(colored(f"   {description}", "blue"))
          print_fn(colored("   Keywords: ", "blue"))
          print_fn(colored(f"  {', '.join(keywords)}", "blue"))

        except:
          print_fn(colored("[-] Error generating metadata", "red"))

        if automate_youtube_upload:
            # Start Youtube Uploader
            # Check if the CLIENT_SECRETS_FILE exists
            client_secrets_file = os.path.abspath("./client_secret.json")
            SKIP_YT_UPLOAD = False
            if not os.path.exists(client_secrets_file):
                SKIP_YT_UPLOAD = True
                print_fn(colored("[-] Client secrets file missing. YouTube upload will be skipped.", "yellow"))
                print_fn(colored("[-] Please download the client_secret.json from Google Cloud Platform and store this inside the /Backend directory.", "red"))

            # Only proceed with YouTube upload if the toggle is True  and client_secret.json exists.
            if not SKIP_YT_UPLOAD:
                # Choose the appropriate category ID for your videos
                video_category_id = "28"  # Science & Technology
                privacyStatus = "private"  # "public", "private", "unlisted"
                video_metadata = {
                    'video_path': os.path.abspath(f"../temp/{final_video_path}"),
                    'title': title,
                    'description': description,
                    'category': video_category_id,
                    'keywords': ",".join(keywords),
                    'privacyStatus': privacyStatus,
                }

                # Upload the video to YouTube
                try:
                    # Unpack the video_metadata dictionary into individual arguments
                    video_response = upload_video(
                        video_path=video_metadata['video_path'],
                        title=video_metadata['title'],
                        description=video_metadata['description'],
                        category=video_metadata['category'],
                        keywords=video_metadata['keywords'],
                        privacy_status=video_metadata['privacyStatus']
                    )
                    print_fn(f"Uploaded video ID: {video_response.get('id')}")
                except HttpError as e:
                    print_fn(f"An HTTP error {e.resp.status} occurred:\n{e.content}")

        video_clip = VideoFileClip(f"../temp/{final_video_path}")
        if use_music:
            # Select a random song
            song_path = choose_random_song()

            # Add song to video at 30% volume using moviepy
            original_duration = video_clip.duration
            original_audio = video_clip.audio
            song_clip = AudioFileClip(song_path).set_fps(44100)

            # Set the volume of the song to 10% of the original volume
            song_clip = song_clip.volumex(0.1).set_fps(44100)

            # Add the song to the video
            comp_audio = CompositeAudioClip([original_audio, song_clip])
            video_clip = video_clip.set_audio(comp_audio)
            video_clip = video_clip.set_fps(30)
            video_clip = video_clip.set_duration(original_duration)
            video_clip.write_videofile(f"../{final_video_path}", threads=n_threads or 1)
        else:
            video_clip.write_videofile(f"../{final_video_path}", threads=n_threads or 1)


        # Let user know
        print_fn(colored(f"[+] Video generated: {final_video_path}!", "green"))

        # Stop FFMPEG processes
        if os.name == "nt":
            # Windows
            os.system("taskkill /f /im ffmpeg.exe")
        else:
            # Other OS
            os.system("pkill -f ffmpeg")

        GENERATING = False

        # Return JSON
        return jsonify(
            {
                "status": "success",
                "message": "Video generated! See MoneyPrinter/output.mp4 for result.",
                "data": final_video_path,
            }
        )
    except Exception as err:
        print_fn(colored(f"[-] Error: {str(err)}", "red"))
        return jsonify(
            {
                "status": "error",
                "message": f"Could not retrieve stock videos: {str(err)}",
                "data": [],
            }
        )

