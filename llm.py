import requests

API_KEY = "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"

def generate_response(prompt):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # ✅ free/cheap & powerful
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"ERROR: {str(e)}"
