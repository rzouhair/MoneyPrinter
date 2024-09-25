from venv import logger
import requests

from typing import List
from termcolor import colored

# from Backend.main import generate_image

def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.

    Returns:
        List[str]: A list of stock videos.
    """
    
    # Build URL
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={it}"

    logger.info("Before request")
    # Send the request

    payload = {}
    headers = {
      'Authorization': 'ZW7nMLprvXyJub29QkWBYcfemuRxE9rUbtejdrLLm52snO2TbwQzED2k',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    r = requests.request("GET", qurl, headers=headers, data=payload)
    # r = requests.get(qurl, headers=headers)
    logger.info(r.text)
    logger.info("After request: " + api_key)

    # Parse the response
    response = r.json()

    # Parse each video
    raw_urls = []
    video_url = []
    video_res = 0

    logger.info("Looking for stock videos")
    try:
        # loop through each video in the result
        for i in range(it):
            #check if video has desired minimum duration
            if response["videos"][i]["duration"] < min_dur:
                continue
            raw_urls = response["videos"][i]["video_files"]
            temp_video_url = ""
            
            # loop through each url to determine the best quality
            for video in raw_urls:
                # Check if video has a valid download link
                if ".com/video-files" in video["link"]:
                    # Only save the URL with the largest resolution
                    if (video["width"]*video["height"]) > video_res:
                        temp_video_url = video["link"]
                        video_res = video["width"]*video["height"]
                        
            # add the url to the return list if it's not empty
            if temp_video_url != "":
                video_url.append(temp_video_url)
                
    except Exception as e:
        print(colored("[-] No Videos found.", "red"))
        print(colored(e, "red"))

    # Let user know
    print(colored(f"\t=> \"{query}\" found {len(video_url)} Videos", "cyan"))

    # Return the video url
    return video_url


def search_for_stock_images(query: str, api_key: str, it: int) -> List[str]:
    """
    Searches for stock images based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.

    Returns:
        List[str]: A list of stock images.
    """
    
    # Build URL
    """ qurl = f"https://api.pexels.com/v1/search?query={query}&per_page={it}"

    logger.info("Before request") """
    # Send the request

    """ payload = {}
    headers = {
      'Authorization': 'ZW7nMLprvXyJub29QkWBYcfemuRxE9rUbtejdrLLm52snO2TbwQzED2k',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    r = requests.request("GET", qurl, headers=headers, data=payload) """
    # r = requests.get(qurl, headers=headers)
    # logger.info("After request: " + api_key)

    # Parse the response
    # response = r.json()

    # image_resp = generate_image(query)

    # Parse each video
    raw_urls = []
    photos_urls = []

    logger.info("Looking for stock images")
    try:
        # loop through each video in the result
        for i in range(it):
            #check if video has desired minimum duration
            # raw_urls = image_resp["data"][0]["url"]
            photos_urls.append(raw_urls)
                
    except Exception as e:
        print(colored("[-] No Videos found.", "red"))
        print(colored(e, "red"))

    # Let user know
    print(colored(f"\t=> \"{query}\" found {len(photos_urls)} Videos", "cyan"))

    # Return the video url
    return photos_urls
