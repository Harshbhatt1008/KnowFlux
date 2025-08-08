import prompts
import os
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

github_url = input("Github URL: ").replace("https://github.com/","https://uithub.com/") +"?accept=text%2Fplain&maxTokens=5000"

repo_code = requests.get(github_url).text

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content" : prompts.system_prompt_reviewer,
        },
        {
            "role": "user",
            "content": f"Please provide the review as mentioned for the code repository given below:\n{repo_code}",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)