import openai
from django.conf import settings

# Set the OpenAI API key
openai.api_key = settings.OPENAI_API_KEY


def analyze_email(content):
    """
    Categorizes email content into 'Interested', 'Not Interested', or 'More Information'
    based on keyword matching.
    """
    content = content.lower()

    if "interested" in content:
        return "Interested"
    elif "not interested" in content:
        return "Not Interested"
    elif "more information" in content or "details" in content:
        return "More Information"
    else:
        return "Uncategorized"
def generate_reply(content):
    """
    Generates a simple professional response based on email content.
    """
    if "interested" in content.lower():
        return "Thank you for your interest. We'll get back to you with more details."
    elif "not interested" in content.lower():
        return "Thank you for your response. We respect your decision and wish you the best."
    elif "more information" in content.lower():
        return "Thank you for reaching out. Here is the additional information you requested..."
    else:
        return "Thank you for your email. Could you please provide more details?"


"""""

def analyze_email(content):
   
    Categorizes email content into 'Interested', 'Not Interested', or 'More Information'.
    
    prompt = (
        f"Categorize this mail content as 'Interested', 'Not Interested', or 'More Information':\n\n{content}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-instruct",  # Use the appropriate model
        messages=[
            {"role": "system", "content": "You are an assistant that classifies emails."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=10,
        temperature=0.7,
    )

    return response['choices'][0]['message']['content'].strip()


def generate_reply(content):
    
    Generates a professional response based on the email content.
    
    prompt = f"Based on the context of this email, create a professional response:\n\n{content}"

    response = openai.ChatCompletion.create(




        model="gpt-3.5-turbo-instruct",  # Use the appropriate model
        messages=[
            {"role": "system", "content": "You are an assistant that generates professional email responses."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=10,
        temperature=0.7,
    )

    return response['choices'][0]['message']['content'].strip()
"""""