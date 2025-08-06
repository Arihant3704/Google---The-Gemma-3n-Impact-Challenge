import requests
import json
import os

def get_project_context(project_root_path):
    readme_path = os.path.join(project_root_path, "README.md")
    project_md_path = os.path.join(project_root_path, "PROJECT.md")
    
    context = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r") as f:
            context += "## README.md\n" + f.read() + "\n\n"
    if os.path.exists(project_md_path):
        with open(project_md_path, "r") as f:
            context += "## PROJECT.md\n" + f.read() + "\n\n"
    return context

def chat_with_ollama(prompt, model_name="gemma3n:e4b", ollama_url="http://localhost:11434/api/generate", context=""):
    headers = {"Content-Type": "application/json"}
    
    full_prompt = f"""You are a helpful assistant that knows about the QCar Agent Project. Use the following project documentation to answer questions. If the answer is not in the documentation, state that you don't know. 

Project Documentation:
{context}

User Question: {prompt}

Answer:"""

    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": True
    }

    try:
        response = requests.post(ollama_url, headers=headers, data=json.dumps(payload), stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        full_response_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line)
                    if "response" in json_response:
                        full_response_content += json_response["response"]
                    elif "error" in json_response:
                        print(f"Ollama Error: {json_response['error']}")
                        return None
                except json.JSONDecodeError:
                    # This can happen if a line is incomplete JSON, especially at the end of a stream
                    pass # Ignore incomplete lines
        return full_response_content
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama at {ollama_url}. Is Ollama running?")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

if __name__ == "__main__":
    project_path = "/home/arihant/Desktop/Python qcar application-20250801T132822Z-1-001/test code -20250804T055133Z-1-001/test code /qcar_agent_project/"
    project_context = get_project_context(project_path)

    if not project_context:
        print("Warning: Could not load project documentation. Chatbot will have limited knowledge.")

    print("QCar Project Chatbot (Type 'exit' to quit)")
    while True:
        user_question = input("You: ")
        if user_question.lower() == 'exit':
            break
        
        print("Bot: ", end="")
        response = chat_with_ollama(user_question, context=project_context)
        if response:
            print(response)
        else:
            print("I couldn't get a response from Ollama.")
