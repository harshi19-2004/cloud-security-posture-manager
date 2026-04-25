
import os
from dotenv import load_dotenv

load_dotenv()


def test_groq_connection():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print(" GROQ_API_KEY not set. Add it to your .env file.")
        return

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": "Reply with only: OK"}],
            temperature=0.0,
            max_tokens=10,
        )
        reply = response.choices[0].message.content.strip()
        print(f"✅ Groq API connected. Model replied: {reply}")
    except Exception as e:
        print(f" Groq API error: {e}")


if __name__ == "__main__":
    test_groq_connection()