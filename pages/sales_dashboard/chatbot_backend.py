from openai import OpenAI
import time
import json
import os

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

instructions = """You are a data analyst and chart design expert helping users build charts and answer questions in a fashion brand.

Ensure you answer the user's question accurately and given the context of the dataset. 

Address the user directly as they can see your response.

You should answer the user's question using graphs as much as possible.

The data needed is in the csv files I uploaded, and its 'created_at' is the column with date information.
"""



def create_assistant(client, instructions):
    file = client.files.create(
        file=open("data.csv", "rb"),
        purpose='assistants'
    )
    assistant = client.beta.assistants.create(
        name="AI Assistant",
        instructions=instructions,
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id]
    )
    return assistant

def get_assistant(client, assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

def create_new_thread(client):
    empty_thread = client.beta.threads.create()
    return empty_thread

def get_thread(client, thread_id):
    thread = client.beta.threads.retrieve(thread_id)
    return thread

def add_message(client, thread, content):
    thread_message = client.beta.threads.messages.create(
    thread_id = thread.id,
    role="user",
    content=content,
    )
    return thread_message


def run_chat(client, thread, assistant):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
    
    run = wait_on_run(run, thread)

def show_json(obj):
    return json.loads(obj.model_dump_json())


# assistant = create_assistant(client, instructions)

assistant = get_assistant(client, "asst_muM9FeZZQtW30ojqKCNfo9UK")



if __name__ == "__main__":
    thread = create_new_thread(client)
    print(thread.id)

    user_input = "how are you today?"
    add_message(client, thread, user_input)
    run_chat(client, thread, assistant)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages)