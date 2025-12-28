"""
Email Client - Sends workout notifications

Uses SendGrid API with Gmail SMTP fallback.
"""

import os
from typing import Optional

from config import SENDGRID_API_KEY, EMAIL_RECIPIENT


def send_email(
    recipient: str,
    subject: str,
    body: str,
    sheet_link: Optional[str] = None,
) -> dict:
    """
    Send an email using SendGrid.
    
    Args:
        recipient: Email address to send to
        subject: Email subject
        body: Email body (HTML or plain text)
        sheet_link: Optional Google Sheets link to include
    
    Returns:
        Dict with success status and message
    """
    if not SENDGRID_API_KEY:
        return {"success": False, "error": "SENDGRID_API_KEY not configured"}
    
    if not recipient:
        return {"success": False, "error": "No recipient specified"}
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Content
        
        # Add sheet link to body if provided
        if sheet_link:
            body += f"\n\n---\n📊 **Log your workout:** {sheet_link}"
        
        # Create message
        message = Mail(
            from_email="fitness-agent@noreply.com",
            to_emails=recipient,
            subject=subject,
            html_content=convert_markdown_to_html(body),
        )
        
        # Send
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "Email sent successfully"
        }
        
    except ImportError:
        return {"success": False, "error": "sendgrid package not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to basic HTML for email.
    
    Args:
        markdown_text: Markdown formatted text
    
    Returns:
        HTML formatted text
    """
    html = markdown_text
    
    # Headers
    import re
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Code blocks
    html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = html.replace('\n', '<br>')
    
    # Wrap in paragraph
    html = f'<p>{html}</p>'
    
    # Tables (basic)
    lines = html.split('<br>')
    in_table = False
    new_lines = []
    for line in lines:
        if '|' in line and not in_table:
            in_table = True
            new_lines.append('<table border="1" cellpadding="5">')
        if in_table and '|' in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if all(c.replace('-', '') == '' for c in cells):
                continue  # Skip separator row
            row = '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
            new_lines.append(row)
        elif in_table and '|' not in line:
            in_table = False
            new_lines.append('</table>')
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    if in_table:
        new_lines.append('</table>')
    
    return '<br>'.join(new_lines)


def send_workout_email(
    workout_email: str,
    eval_append: str,
    date: str,
    day_type: str,
    sheet_link: Optional[str] = None,
    is_warning: bool = False,
) -> dict:
    """
    Send workout notification email.
    
    Args:
        workout_email: Workout content from Generator
        eval_append: Eval scores to append (from Eval Agent)
        date: Workout date
        day_type: Workout day type
        sheet_link: Google Sheets link for logging
        is_warning: If True, adds warning banner (3 failed evals)
    
    Returns:
        Dict with success status
    """
    recipient = EMAIL_RECIPIENT
    if not recipient:
        return {"success": False, "error": "EMAIL_RECIPIENT not configured"}
    
    # Build subject
    if is_warning:
        subject = f"⚠️ {date} — {day_type} (Did Not Pass Eval)"
    else:
        subject = f"💪 {date} — {day_type}"
    
    # Build body
    body_parts = []
    
    if is_warning:
        body_parts.append("# ⚠️ WARNING: This workout did not pass quality check")
        body_parts.append("")
        body_parts.append("Review the eval feedback at the bottom and use your judgment.")
        body_parts.append("")
        body_parts.append("---")
        body_parts.append("")
    
    body_parts.append(workout_email)
    body_parts.append(eval_append)
    
    body = "\n".join(body_parts)
    
    return send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        sheet_link=sheet_link,
    )


