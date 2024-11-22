import django_rq
from app.openai_service import analyze_email, generate_reply

# Get the default queue from django_rq
queue = django_rq.get_queue('default')

def process_email(email_content):
    """""
    This function processes an email, categorizing it and generating a reply.
    It adds the task to the RQ queue for background processing."""""

    job = queue.enqueue(_process_email, email_content)
    return job.id  # Return job ID for tracking

def _process_email(email_content):
    """
    Helper function that does the actual email processing. This will run as a background job.
    """
    category = analyze_email(email_content)
    reply = generate_reply(email_content)
    return {"category": category, "reply": reply}
