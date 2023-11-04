import sys
import re
import requests

def extract_form_id(url):
    # Extract formId from the provided URL
    match = re.search(r'/forms/d/([a-zA-Z0-9_-]+)/', url)
    if match:
        return match.group(1)
    else:
        print("Invalid form URL")
        return None

def get_form_responses(form_id, auth_token):
    url = f"https://forms.googleapis.com/v1/forms/{form_id}/responses"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        form_json = response.json()
        return form_json
    else:
        print(response)
        print(f"Failed to fetch form responses. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <formUrl> <token>")
        sys.exit(1)

    form_url = sys.argv[1]
    form_id = extract_form_id(form_url)

    # You can obtain the auth token through the appropriate authentication process
    auth_token = sys.argv[2]

    print()
    print()
    print(form_id)
    print()
    print()
    print(auth_token)
    print()
    print()
    form_json = get_form_responses(form_id, auth_token)

    if form_json:
        print("Form JSON:")
        print(form_json)

