import requests
import json

def generate_birthday_prompt():
    POKE_API_KEY = 'pk_uWXjFJQegHyVq5mZuS7ljem1xJDJfZMk2OwbiiVeTMQ'
    CLAUDE_API_KEY = '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'


    with open("history.txt", "r", encoding="utf-8") as f:
        history = f.read()


    url_knot = "https://development.knotapi.com/transactions/sync"
    headers_knot = {
        "Authorization": "Basic ZGRhMDc3OGQtOTQ4Ni00N2Y4LWJkODAtNmYyNTEyZjliY2RiOjg4NGQ4NGU4NTUwNTRjMzJhOGUzOWQwOGZjZDk4NDVk",  # replace with your real encoded value
        "Content-Type": "application/json"
    }
    data_knot = {
        "merchant_id": 44,
        "external_user_id": "abc",
        "cursor": "eyJpZCI6MjI3ODEsIl9wb2ludHNUb05leHRJdGVtcyI6dHJ1ZX0",
        "limit": 5
    }
    knot_response = requests.post(url_knot, headers=headers_knot, data=json.dumps(data_knot))

    purchase_history = str(knot_response.json()['data'])

    print("Status Code:", response.status_code)
    print("Response Body:", response.text)


    CLAUDE_MESSAGE = '''given my search history: ''' + history + '''\n\n 
    and my purchase history: \n\n ''' + purchase_history + '''\n\n give 
    me a list of 10 items that i want (based on the items i have searched 
    for in the past that i have not yet purchased) '''

    claude_response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'Authorization': f'Bearer {CLAUDE_API_KEY}'
        },
        json={
            'model': 'claude-3-5-sonnet-20240620',
            'messages': [
                {
                    'role': 'user',
                    'content': CLAUDE_MESSAGE
                }
            ]
        }
    )

    print(claude_response.json())
    birthday_gift_list = str(claude_response.json()['content'][0]['text'])

    POKE_MESSAGE = '''for each item on the following list, send an email to one of my 
    friends (one email per friend) telling them that the email is being sent from my 
    assistant, and that you have a suggestion for them for a birthday present 
    they should give me if they don't know what to get. the email should suggest 
    they get that item gently. \n''' + birthday_gift_list

    return POKE_MESSAGE

    '''

    poke_response = requests.post(
        'https://poke.com/api/v1/inbound-sms/webhook',
        headers={
            'Authorization': f'Bearer {POKE_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={'message': POKE_MESSAGE}
    )

    print(poke_response.json())
    '''