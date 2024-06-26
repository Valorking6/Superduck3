import gradio as gr
import requests
import os
import tempfile
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='gradio.analytics')

# Define the API endpoint
API_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

# Define a variable to store the API key
api_key = ""

def set_api_key(key):
    global api_key
    api_key = key
    # Save the API key to a file
    with open("api_key.txt", "w") as file:
        file.write(api_key)

def get_api_key():
    global api_key
    # Check if the API key file exists
    if os.path.exists("api_key.txt"):
        # Read the API key from the file
        with open("api_key.txt", "r") as file:
            api_key = file.read()
    else:
        # Ask the user to enter the API key
        api_key = input("Please enter your API key: ")
        set_api_key(api_key)

def generate_image(prompt, aspect_ratio="1:1", mode="text-to-image", negative_prompt="", model="sd3", seed=0, output_format="png"):
    headers = {
        "authorization": f"Bearer {api_key}",
        "accept": "image/*" if output_format != "json" else "application/json"
    }
    data = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "negative_prompt": negative_prompt,
        "model": model,
        "seed": seed,
        "output_format": output_format
    }
    # Filter out None values
    data = {k: v for k, v in data.items() if v is not None}
    # Make the POST request
    response = requests.post(API_ENDPOINT, headers=headers, files={"none": ''}, data=data)
    # Process the response
    if response.status_code == 200:
        if output_format == "json":
            return response.json()
        else:
            # Save the image bytes to a temporary file and return the file path
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}") as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            return temp_file_path
    else:
        return f"Error: {response.json()}"

# Define the Gradio interface
def launch_interface():
    output_format = gr.Dropdown(label="Output Format", choices=["png", "jpeg", "json"], value="png")
    
    iface = gr.Interface(
        fn=generate_image,
        inputs=[
            gr.Textbox(label="Prompt", placeholder="Enter your prompt"),
            gr.Dropdown(label="Aspect Ratio", choices=["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"], value="1:1"),
           gr.Dropdown(label="Mode", choices=["text-to-image"], value="text-to-image"),
            gr.Textbox(label="Negative Prompt", placeholder="Enter your negative prompt"),
            gr.Dropdown(label="Model", choices=["sd3", "sd3-turbo"], value="sd3"),
            gr.Number(label="Seed"),
            output_format
        ],
        outputs=[gr.Image(type="filepath") if output_format.value != "json" else gr.JSON()],
        title="SuperDuck3 API Interface",
        description="This interface allows you to generate images using the Stability AI API."
    )

    # Launch the Gradio web UI
    iface.launch(inbrowser=True)

# Get the API key
get_api_key()

# Run the Gradio interface
launch_interface()
