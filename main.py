import os
from diffusers import StableDiffusionInstructPix2PixPipeline
from PIL import Image
import torch

# Function to get user input with validation
def get_image_path():
    while True:
        path = input("Enter the path to the input image: ").strip()
        if os.path.exists(path) and path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return path
        print("Invalid file path or unsupported format. Please try again.")

# Function to resize large images for processing
def resize_image(image, max_size=1024):
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)  # Updated resampling
        print(f"Image resized to: {new_size}")
    return image

# Function to log messages to a file
def log_message(message, log_file="process_log.txt"):
    with open(log_file, "a") as log:
        log.write(message + "\n")

# Load the model
def load_model():
    print("Loading InstructPix2Pix model...")
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = StableDiffusionInstructPix2PixPipeline.from_pretrained(
            "timbrooks/instruct-pix2pix", 
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        print(f"Model loaded successfully on {device}")
        return model
    except Exception as e:
        log_message(f"Error loading model: {e}")
        print(f"Error loading model: {e}")
        exit()

# Generate multiple outputs
def generate_outputs(model, input_image, prompt, num_outputs):
    outputs = []
    for i in range(num_outputs):
        print(f"Generating output {i + 1}/{num_outputs}...")
        output = model(
            image=input_image,
            prompt=prompt,
            num_inference_steps=50,
            guidance_scale=7.5
        ).images[0]
        outputs.append(output)
    return outputs

# Main script
def main():
    model = load_model()

    # Ask the user for a single image or a batch of images
    mode = input("Do you want to process a single image or a batch of images? (single/batch): ").strip().lower()
    if mode == "batch":
        folder_path = input("Enter the folder path containing images: ").strip()
        if not os.path.exists(folder_path):
            print("Invalid folder path. Exiting...")
            return
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_image = Image.open(file_path).convert("RGB")
                input_image = resize_image(input_image)
                prompt = input(f"Enter the modification for {filename}: ")
                num_outputs = int(input("How many variations would you like to generate? "))
                outputs = generate_outputs(model, input_image, prompt, num_outputs)
                for i, output in enumerate(outputs):
                    output_path = f"edited_{i + 1}_{filename}"
                    output.save(output_path)
                    print(f"Saved: {output_path}")
    else:
        input_image_path = get_image_path()
        input_image = Image.open(input_image_path).convert("RGB")
        input_image = resize_image(input_image)
        print(f"Loaded input image with size: {input_image.size}")
        prompt = input("Enter the modification you'd like to make to the image: ")
        num_outputs = int(input("How many variations would you like to generate? "))

        # Generate the modified images
        outputs = generate_outputs(model, input_image, prompt, num_outputs)
        for i, output in enumerate(outputs):
            output_path = f"edited_{i + 1}_{os.path.basename(input_image_path)}"
            output.save(output_path)
            print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
