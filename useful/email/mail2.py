#!/usr/bin/env python3
import json
import csv
import argparse
import os
import http.client
import json
import sys
from typing import Dict, List, Union
from string import Formatter

try:
    import markdown
    from markdown.extensions import fenced_code
    from markdown.extensions import tables
    from markdown.extensions import attr_list
except ImportError:
    print("Installing required markdown package...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown
    from markdown.extensions import fenced_code
    from markdown.extensions import tables
    from markdown.extensions import attr_list

def convert_markdown_to_html(content: str) -> str:
    """
    Convert markdown content to HTML.
    """
    html = markdown.markdown(content, extensions=[
        'fenced_code',
        'tables',
        'attr_list'
    ])
    
    # Add some basic styling
    styled_html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        {html}
    </div>
    """
    return styled_html

def validate_template_keys(template: str, data: dict) -> List[str]:
    """
    Validate that all format specifiers in the template have matching keys in data.
    Returns list of missing keys.
    """
    required_keys = {
        fname for _, fname, _, _ in Formatter().parse(template) 
        if fname is not None
    }
    return [key for key in required_keys if key not in data]

def format_with_fallback(template: str, data: dict, fallback: str = '') -> str:
    """
    Format string with dict data, replacing missing values with fallback.
    """
    class DefaultDict(dict):
        def __missing__(self, key):
            return fallback
    
    try:
        return template.format_map(DefaultDict(data))
    except ValueError as e:
        print(f"Warning: Format error in template: {e}", file=sys.stderr)
        return template

def send_email(
    to_email: str,
    subject: str,
    content: str,
    from_email: str,
    is_markdown: bool = False,
    api_key: str = None,
    template_data: dict = None
) -> bool:
    """
    Send a single email using SendGrid's API.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Email body content (can include format specifiers)
        from_email: Sender email address
        is_markdown: Whether the content is Markdown (default: False)
        api_key: SendGrid API key (defaults to env variable)
        template_data: Dictionary of values to format the content with
    """
    if not api_key:
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            raise ValueError("No SendGrid API key provided")

    # Format content and subject if template_data provided
    if template_data:
        content = format_with_fallback(content, template_data)
        subject = format_with_fallback(subject, template_data)
    
    # Convert markdown to HTML if needed
    if is_markdown:
        content = convert_markdown_to_html(content)
        is_html = True
    else:
        is_html = False

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}]
            }
        ],
        "from": {"email": from_email},
        "subject": subject,
        "content": [
            {
                "type": "text/html" if is_html else "text/plain",
                "value": content
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        conn = http.client.HTTPSConnection("api.sendgrid.com")
        conn.request(
            "POST",
            "/v3/mail/send",
            body=json.dumps(payload),
            headers=headers
        )
        
        response = conn.getresponse()
        conn.close()
        
        if response.status == 202:
            return True
            
        error_msg = response.read().decode()
        print(f"SendGrid API error (status {response.status}): {error_msg}", file=sys.stderr)
        return False
            
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False

def load_data(filepath: str) -> List[Dict]:
    """
    Load data from either CSV or JSON file.
    """
    if filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            return json.load(f)
    elif filepath.endswith('.csv'):
        data = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    else:
        raise ValueError("Unsupported file format. Use .json or .csv")

def main():
    parser = argparse.ArgumentParser(description='Send emails using SendGrid API')
    parser.add_argument('--src', type=str, help='Source file path (CSV or JSON)')
    parser.add_argument('--to', type=str, help='Recipient email (for single email)')
    parser.add_argument('--from', dest='from_email', type=str, required=True,
                      help='Sender email address')
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--content', type=str, help='Email content')
    parser.add_argument('--markdown', action='store_true', help='Treat content as Markdown')
    parser.add_argument('--template', type=str, help='Template file for email content')
    parser.add_argument('--api-key', type=str, help='SendGrid API key (optional, defaults to SENDGRID_API_KEY env var)')
    parser.add_argument('--validate', action='store_true', help='Validate templates without sending')
    parser.add_argument('--preview', action='store_true', help='Preview the first email content without sending')
    
    args = parser.parse_args()
    
    # Handle template if provided
    template_content = None
    if args.template:
        with open(args.template, 'r') as f:
            template_content = f.read()
    
    # Single email mode
    if args.to:
        content = template_content if template_content else args.content
        if not content:
            raise ValueError("Either --content or --template must be provided")
            
        success = send_email(
            args.to,
            args.subject,
            content,
            args.from_email,
            args.markdown,
            args.api_key
        )
        print(f"Email {'sent successfully' if success else 'failed'}")
        return
    
    # Batch mode
    if not args.src:
        raise ValueError("Either --to or --src must be provided")
        
    data = load_data(args.src)
    success_count = 0
    
    # Get base template content
    content = template_content if template_content else args.content
    
    # Preview mode
    if args.preview and data:
        print("\nPreview of first email:")
        preview_content = format_with_fallback(content, data[0])
        if args.markdown:
            print("\nMarkdown content:")
            print("-" * 40)
            print(preview_content)
            print("\nConverted HTML:")
            print("-" * 40)
            print(convert_markdown_to_html(preview_content))
        else:
            print(preview_content)
        return

    # Validate templates if requested
    if args.validate:
        print("Validating templates...")
        for item in data:
            missing_keys = validate_template_keys(content, item)
            if missing_keys:
                print(f"Warning: Missing keys for {item.get('to_email', 'unknown recipient')}: {missing_keys}")
            if args.subject:
                missing_subject_keys = validate_template_keys(args.subject, item)
                if missing_subject_keys:
                    print(f"Warning: Missing subject keys for {item.get('to_email', 'unknown recipient')}: {missing_subject_keys}")
        return

    # Send emails
    for item in data:
        if 'to_email' not in item:
            print(f"Skipping record: missing to_email field", file=sys.stderr)
            continue
            
        success = send_email(
            item['to_email'],
            args.subject,
            content,
            args.from_email,
            args.markdown,
            args.api_key,
            template_data=item
        )
        
        if success:
            success_count += 1
            
    print(f"Batch complete: {success_count}/{len(data)} emails sent successfully")

if __name__ == "__main__":
    main()
