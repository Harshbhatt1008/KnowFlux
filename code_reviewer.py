# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
import prompts
import requests
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
github_url = input("Github URL: ").replace("https://github.com/","https://uithub.com/") +"?accept=text%2Fplain"

repo_code = requests.get(github_url).text

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-pro"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"Please provide the review as mentioned for the code repository given below:\n{repo_code}"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=prompts.system_prompt_reviewer),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
