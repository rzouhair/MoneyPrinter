import re
import os
from venv import logger
from flask import jsonify
import g4f
import json
import openai
import google.generativeai as genai

from g4f.client import Client
from termcolor import colored
from dotenv import load_dotenv
from typing import Tuple, List

# Load environment variables
load_dotenv("../.env")

# Set environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


def generate_response(prompt: str, ai_model: str,) -> str:
    """
    Generate a script for a video, depending on the subject of the video.

    Args:
        video_subject (str): The subject of the video.
        ai_model (str): The AI model to use for generation.


    Returns:

        str: The response from the AI model.

    """

    if ai_model == 'g4f':
        # Newest G4F Architecture
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            provider=g4f.Provider.You, 
            messages=[{"role": "user", "content": prompt}],
        ).choices[0].message.content

    elif ai_model in ["gpt3.5-turbo", "gpt4"]:

        model_name = "gpt-3.5-turbo" if ai_model == "gpt3.5-turbo" else "gpt-4o-mini"

        response = openai.chat.completions.create(

            model=model_name,

            messages=[{"role": "user", "content": prompt}],

        ).choices[0].message.content
    elif ai_model == 'gemmini':
        model = genai.GenerativeModel('gemini-pro')
        response_model = model.generate_content(prompt)
        response = response_model.text

    else:

        raise ValueError("Invalid AI model selected.")

    return response

def generate_script(video_subject: str, paragraph_number: int, ai_model: str, voice: str, customPrompt: str) -> str:

    """
    Generate a script for a video, depending on the subject of the video, the number of paragraphs, and the AI model.



    Args:

        video_subject (str): The subject of the video.

        paragraph_number (int): The number of paragraphs to generate.

        ai_model (str): The AI model to use for generation.



    Returns:

        str: The script for the video.

    """

    # Build prompt
    
    if customPrompt:
        prompt = customPrompt
    else:
        prompt = """
            Generate a script for a video, depending on the subject of the video.

            The script is to be returned as a string with the specified number of paragraphs.

            Here is an example of a string:
            "This is an example string."

            Do not under any circumstance reference this prompt in your response.

            Get straight to the point, don't start with unnecessary things like, "welcome to this video".

            Obviously, the script should be related to the subject of the video.

            YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
            YOU MUST WRITE THE SCRIPT IN THE LANGUAGE SPECIFIED IN [LANGUAGE].
            ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT.

        """

    prompt += f"""
    
    Subject: {video_subject}
    Number of paragraphs: {paragraph_number}
    Language: {voice}

    """

    # Generate script
    response = generate_response(prompt, ai_model)

    print(colored(response, "cyan"))

    # Return the generated script
    if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        logger.info(colored(f"Response: {response}", "blue"))
        paragraphs_function = {
          "name": "extract_paragraphs",
          "description": "Extract the paragraphs from the script.",
          "parameters": {
            "type": "object",
            "properties": {
              "paragraphs": {
                "type": "array",
                "description": "The list of paragraphs extracted",
                "items": {
                  "type": "string",
                  "description": "The extracted paragraph"
                }
              },
            },
          }
        }

        logger.info("Extracting paragraphs")
        paragraphs = chat_scaffold([
            {"role": "user", "content": f"""
Given the following script, extract the paragraphs in a clean format without any markdown or other formatting. and without changing the original script.
          
Script:
{response}
"""},
        ], 'gpt-4o-mini', paragraphs_function)

        logger.info("Selecting the specified number of paragraphs " + str(paragraph_number))
        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs['content']['paragraphs'][:paragraph_number]

        logger.info(colored(f"Selected paragraphs: {selected_paragraphs}", "blue"))

        print(colored(f"Number of paragraphs used: {len(selected_paragraphs)}", "green"))

        # Join the selected paragraphs into a single string
        final_script = "\n\n".join(selected_paragraphs)

        # Print to console the number of paragraphs used
        print(colored(f"Number of paragraphs used: {len(selected_paragraphs)}", "green"))

        return final_script
    else:
        print(colored("[-] GPT returned an empty response.", "red"))
        return None


def get_search_terms(video_subject: str, amount: int, script: str, ai_model: str) -> List[str]:
    """
    Generate a JSON-Array of search terms for stock videos,
    depending on the subject of a video.

    Args:
        video_subject (str): The subject of the video.
        amount (int): The amount of search terms to generate.
        script (str): The script of the video.
        ai_model (str): The AI model to use for generation.

    Returns:
        List[str]: The search terms for the video subject.
    """

    # Build prompt
    prompt = f"""
    Generate {amount} search terms for stock videos,
    depending on the subject of a video.
    Subject: {video_subject}

    The search terms are to be returned as
    a JSON-Array of strings.

    Each search term should consist of 1-3 words,
    always add the main subject of the video.
    
    YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
    YOU MUST NOT RETURN ANYTHING ELSE. 
    YOU MUST NOT RETURN THE SCRIPT.
    
    The search terms must be related to the subject of the video.
    Here is an example of a JSON-Array of strings:
    ["search term 1", "search term 2", "search term 3"]

    For context, here is the full text:
    {script}
    """

    # Generate search terms
    response = generate_response(prompt, ai_model)
    print(response)

    # Parse response into a list of search terms
    search_terms = []
    
    try:
        search_terms = json.loads(response)
        if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
            raise ValueError("Response is not a list of strings.")

    except (json.JSONDecodeError, ValueError):
        # Get everything between the first and last square brackets
        response = response[response.find("[") + 1:response.rfind("]")]

        print(colored("[*] GPT returned an unformatted response. Attempting to clean...", "yellow"))

        # Attempt to extract list-like string and convert to list
        match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
        print(match.group())
        if match:
            try:
                search_terms = json.loads(match.group())
            except json.JSONDecodeError:
                print(colored("[-] Could not parse response.", "red"))
                return []


    # Let user know
    print(colored(f"\nGenerated {len(search_terms)} search terms: {', '.join(search_terms)}", "cyan"))
    logger.info(colored(f"\nGenerated {len(search_terms)} search terms: {', '.join(search_terms)}", "cyan"))

    # Return search terms
    return search_terms


def generate_metadata(video_subject: str, script: str, ai_model: str) -> Tuple[str, str, List[str]]:  
    """  
    Generate metadata for a YouTube video, including the title, description, and keywords.  
  
    Args:  
        video_subject (str): The subject of the video.  
        script (str): The script of the video.  
        ai_model (str): The AI model to use for generation.  
  
    Returns:  
        Tuple[str, str, List[str]]: The title, description, and keywords for the video.  
    """  
  
    # Build prompt for title  
    title_prompt = f"""  
    Generate a catchy and SEO-friendly title for a YouTube shorts video about {video_subject}.  
    """  
  
    # Generate title  
    title = generate_response(title_prompt, ai_model).strip()  
    
    # Build prompt for description  
    description_prompt = f"""  
    Write a brief and engaging description for a YouTube shorts video about {video_subject}.  
    The video is based on the following script:  
    {script}  
    """  
  
    # Generate description  
    description = generate_response(description_prompt, ai_model).strip()  
  
    # Generate keywords  
    keywords = get_search_terms(video_subject, 6, script, ai_model)  

    return title, description, keywords  

def chat_scaffold(messages, ai_model, function_call=None):
  logger.info(openai)
  resp = openai.chat.completions.create(
    model=ai_model or 'gpt-4o-mini',
    messages=messages,
  ) if not function_call else openai.chat.completions.create(
    model=ai_model or 'gpt-4o-mini',
    messages=messages,
    tools=[
        {"type": "function", "function": function_call}
    ],
  )

  tool_call = resp.choices[0].message.tool_calls[0]
  content = None
  if (tool_call and function_call):
    arguments = json.loads(tool_call.function.arguments)
    content = arguments
  else:
    content = resp.choices[0].message.content

  print("==========")
  print(content)
  print("==========")

  return {
    "content": content
  }

def generate_motivational_video_script(quote = None, additional_prompt = ''):

  final_quote = ''
  if quote:
     final_quote = f"""
For the following quote:
{quote}
"""
  else:
     final_quote = f"""
Pick a motivation quote from one of the motivational books using this template:
"[quote]": [author] - [book]

and

"""

  prompt = f"""
{final_quote}

create:  
1. A short video script (suitable for TikTok, Reels, or Shorts) that:  
   - Starts directly with the quote  
   - Moves immediately into a clear, concise explanation  
   - Speaks directly to the viewer in simple language appropriate for a 12-year-old  
   - Relates the quote to the viewer's life or experiences  
   - Is approximately 45-90 seconds long
   - The quote shouldn't contain any markdown, asterisks, single or double quotes, or any special characters  
   - Make it like an old man giving a young man advice, without making it obvious, like "listen here" - "my friend, kiddo, listen here" etc...
2. A video caption that:  
   - Mentions the quote and its author/book in this format: "Quote": Author - Book  
   - Provides an additional explanation or insight  
   - Is approximately 100 words long  

{additional_prompt}
Use the following structure for each quote:

## [Quote Number]. [Book Title] by [Author]
### Video Script:
"[Quote]" [Insert 50-75 word explanation here or a 30-90 seconds script]
### Video Caption:
[Insert 25-40 word caption here]

Example output:
## 1. "Atomic Habits" by James Clear
### Video Script:
"You do not rise to the level of your goals. You fall to the level of your systems." Your daily habits shape your future. Big dreams aren't enough; it's the small actions you take every day that matter. Want to improve? Focus on building good routines. Make small, consistent changes in your life. Your everyday choices are creating the person you'll become.
### Video Caption:
James Clear's wisdom from "Atomic Habits" reminds us: success isn't about grand goals, but daily actions. What small habits can you start today to shape your tomorrow? #AtomicHabits #DailyImprovement

The example above isn't exclusive, and not to be taken as a template. The prompt should be modified to suit the specific quote and author/book.
None of the output should have any markdown, asterics, single or double quotes or any special characters.
"""

  script_function = {
    "name": "generate_script",
    "description": "Generate a motivational video script.",
    "parameters": {
      "type": "object",
      "properties": {
        "script": {
          "type": "string",
          "description": "The motivational video script",
        },
        "caption": {
          "type": "string",
          "description": "The motivational video caption",
        }
      },
    }
  }

  response = chat_scaffold([
      {"role": "system", "content": "You are a helpful assistant and professional viral videos content creator that generates motivational videos scripts."},
      {"role": "user", "content": prompt}
  ], 'gpt-4o-mini', script_function)

  return response['content']