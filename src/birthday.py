import requests
import json

def generate_birthday_prompt():

    with open("history.txt", "r", encoding="utf-8") as f:
        history = f.read()


    url = "https://knot.tunnel.tel/transactions/sync"
    headers = {
    "Content-Type": "application/json"
    }
    data = {
        "merchant_id": 44,
        "external_user_id": "abc",
        "limit": 5
    }

    knot_response = requests.post(url, headers=headers, json=data)

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