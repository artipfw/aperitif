import os

from openai import OpenAI

client = OpenAI(
  api_key = os.environ.get("OPENAI_API_KEY", "fake"),
  base_url="https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Tell me a joke.",
        }
    ],
    model="microsoft/Phi-4-multimodal-instruct",
    max_tokens=30,
)

print(chat_completion.to_json(indent=4))
