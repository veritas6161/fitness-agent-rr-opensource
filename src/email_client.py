"""
Email Client - Sends workout notifications

Uses SendGrid API with Gmail SMTP fallback.
"""

import os
from typing import Optional

from config import SENDGRID_API_KEY, EMAIL_RECIPIENT, SENDER_EMAIL


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
    
    # Determine sender email (must be verified in SendGrid)
    # Use SENDER_EMAIL if set, otherwise use recipient email
    sender_email = SENDER_EMAIL or recipient
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Content
        
        # Add sheet link to body if provided
        if sheet_link:
            body += f"\n\n---\n📊 **Log your workout:** {sheet_link}"
        
        # Create message
        message = Mail(
            from_email=sender_email,
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
        error_msg = str(e)
        # Provide helpful error messages for common SendGrid errors
        if "403" in error_msg or "Forbidden" in error_msg:
            error_msg += "\n\n💡 TIP: SendGrid 403 Forbidden usually means:\n"
            error_msg += "   1. The sender email is not verified in SendGrid\n"
            error_msg += f"   2. Verify '{sender_email}' in SendGrid Settings > Sender Authentication\n"
            error_msg += "   3. Or set SENDER_EMAIL in .env to a verified email address"
        return {"success": False, "error": error_msg}


def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML for email with proper table styling.
    
    Args:
        markdown_text: Markdown formatted text
    
    Returns:
        HTML formatted text with inline styles for consistent rendering
    """
    import re
    
    # Process tables first (before other conversions)
    lines = markdown_text.split('\n')
    processed_lines = []
    in_table = False
    table_lines = []
    
    for line in lines:
        # Check if this is a table row
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                # Start table with styling
                processed_lines.append('<table style="border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 14px;">')
            table_lines.append(line)
        elif in_table:
            # End of table
            # Process accumulated table lines
            if table_lines:
                for i, table_line in enumerate(table_lines):
                    cells = [c.strip() for c in table_line.split('|') if c.strip()]
                    if not cells:
                        continue
                    # Check if separator row
                    if all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                        continue
                    
                    # First row is header
                    if i == 0:
                        row_html = '<tr style="background-color: #f5f5f5; font-weight: bold;">'
                        for cell in cells:
                            row_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{cell}</td>'
                        row_html += '</tr>'
                    else:
                        row_html = '<tr>'
                        for cell in cells:
                            row_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top;">{cell}</td>'
                        row_html += '</tr>'
                    processed_lines.append(row_html)
            processed_lines.append('</table>')
            in_table = False
            table_lines = []
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    # Handle table at end of text
    if in_table and table_lines:
        for i, table_line in enumerate(table_lines):
            cells = [c.strip() for c in table_line.split('|') if c.strip()]
            if not cells:
                continue
            if all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                continue
            if i == 0:
                row_html = '<tr style="background-color: #f5f5f5; font-weight: bold;">'
                for cell in cells:
                    row_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: left;">{cell}</td>'
                row_html += '</tr>'
            else:
                row_html = '<tr>'
                for cell in cells:
                    row_html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top;">{cell}</td>'
                row_html += '</tr>'
            processed_lines.append(row_html)
        processed_lines.append('</table>')
    
    html = '\n'.join(processed_lines)
    
    # Headers with consistent sizing
    html = re.sub(r'^### (.+)$', r'<h3 style="font-size: 16px; font-weight: bold; margin: 15px 0 10px 0; color: #333;">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2 style="font-size: 18px; font-weight: bold; margin: 20px 0 12px 0; color: #222; border-bottom: 2px solid #eee; padding-bottom: 5px;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1 style="font-size: 24px; font-weight: bold; margin: 0 0 15px 0; color: #111;">\1</h1>', html, flags=re.MULTILINE)
    
    # Horizontal rules
    html = re.sub(r'^---$', r'<hr style="border: none; border-top: 2px solid #eee; margin: 20px 0;">', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Blockquotes (Pro Tips)
    html = re.sub(r'^> (.+)$', r'<blockquote style="border-left: 4px solid #4CAF50; padding-left: 15px; margin: 10px 0; color: #555; font-style: italic;">\1</blockquote>', html, flags=re.MULTILINE)
    
    # Code blocks
    html = re.sub(r'```(.+?)```', r'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;"><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 2px;">\1</code>', html)
    
    # Bullet points
    html = re.sub(r'^- (.+)$', r'<li style="margin: 5px 0;">\1</li>', html, flags=re.MULTILINE)
    # Wrap consecutive <li> in <ul>
    html = re.sub(r'(<li[^>]*>.*?</li>(?:\s*<li[^>]*>.*?</li>)*)', r'<ul style="margin: 10px 0; padding-left: 20px;">\1</ul>', html, flags=re.DOTALL)
    
    # Paragraphs - wrap text blocks
    lines = html.split('\n')
    result_lines = []
    current_para = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_para:
                result_lines.append(f'<p style="margin: 10px 0; line-height: 1.6; font-size: 14px;">{" ".join(current_para)}</p>')
                current_para = []
            continue
        
        # Don't wrap HTML tags
        if line.startswith('<'):
            if current_para:
                result_lines.append(f'<p style="margin: 10px 0; line-height: 1.6; font-size: 14px;">{" ".join(current_para)}</p>')
                current_para = []
            result_lines.append(line)
        else:
            current_para.append(line)
    
    if current_para:
        result_lines.append(f'<p style="margin: 10px 0; line-height: 1.6; font-size: 14px;">{" ".join(current_para)}</p>')
    
    html = '\n'.join(result_lines)
    
    # Wrap in container with consistent font
    html = f'<div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333; max-width: 800px;">{html}</div>'
    
    return html


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



