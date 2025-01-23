import tiktoken
from openai import OpenAI
import src.prompt as pr

client = OpenAI(api_key="")
selected_model = "gpt-3.5-turbo-0301"

def setAPI(api_key):
    client.api_key = api_key

def talkWithChatGPT(prompt):
    completion = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()


def chatWithChatGPT(model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": m["role"], "content":m["content"]}
                  for m in messages]
    )
    return response.choices[0].message.content.strip()


def count_tokens(text):
    try:
        encoding = tiktoken.encoding_for_model(selected_model)
        num_tokens = encoding.encode(text)
        return len(num_tokens)
    except:
        return 0


def get_bulletpoint_unknown_knowledge(role, topic, text):
    try:
        summary_prompt = pr.get_bullet_unknown_knowledge.format(
            role=role, topic=topic, InputText=text)
        summary = talkWithChatGPT(summary_prompt)
        return summary
    except:
        return 0


def get_suitable_role(topic):
    try:
        prompt = pr.get_suitable_role.format(InputText=topic)
        response = talkWithChatGPT(prompt)
        return response
    except:
        return 0


def calculate_sum_token(input_text, output_text):
    try:
        return count_tokens(input_text) + count_tokens(output_text)
    except:
        return 0


def extract_paragraph_batches(paragraph, batch_size):
    words = paragraph.split()
    for i in range(0, len(words), batch_size):
        yield " ".join(words[i:i + batch_size])


def extract_words(text, words):
    words = text.split()[:words]
    return ' '.join(words)
