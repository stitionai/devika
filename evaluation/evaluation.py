import json
import requests

def load_tasks():
    with open('./instructions.json', 'r') as file:
        instructions_data = json.load(file)
    return instructions_data

def create_project(name):
    url = "http://localhost:1337/api/create-project"

    # Define the payload
    payload = {
        "project_name": name
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Project creation Request successfully sent\n", "response : ", response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")

def execute(prompt, model, project):
    # Define the URL
    url = "http://localhost:1337/api/execute-agent"

    # Define the payload
    payload = {
        "prompt": prompt,
        "base_model": model,
        "project_name": project
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Agent Execution Request successfully sent, reponse:", response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")

def get_model_list():
    url = "http://localhost:1337/api/model-list"

    # Send the POST request
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        print("Agent Execution Request successfully sent, reponse:", response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
    return response.json()

class Summary():
    def __init__(self):
        self.tokenusage = 0
        self.averagetokenperstep = 0
        self.stepcount=0 
        self.llmcalls=0

if __name__ == '__main__':
    instructions_data = load_tasks()
    instructions = instructions_data['instructions']
    models = get_model_list()
    model = models['models'][5][1]
    print(model)
    
    for idx,i in enumerate(instructions):
        project_name = "testframe" + str(idx)
        print(f"PROMPT{idx + 1}: {i} \n")
        create_project(project_name)
        execute(i,model,project_name)
        