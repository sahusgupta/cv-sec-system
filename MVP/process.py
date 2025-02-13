
import base64
import json
import os
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_frames(frames, criteria):
    """
    
    Parameters:
        frames (list): A list of frame filenames.
        
    Returns:
        dict: A JSON-like dictionary containing the criteria confidences and overall probability.
              Example:
              {
                  "criteria_confidences": {"criteria1": 0.8, "criteria2": 0.5},
                  "overall_probability": 0.65
              }
    """
    api_key = os.environ.get("OPENAI_API_KEY")
        
    client = OpenAI()
    client.api_key = api_key
    
    criteria_confidences = {criterion: [] for criterion in criteria}
    prompt = (
            "You are a video analysis assistant. Analyze the provided image file. "
            "For each image, determine the confidence that certain specified criteria are met. "
            f"The criteria are: {criteria}. "
            "Return a dictionary with two keys: 'final_score' which is the average of the confidence scores for the criteria, and the odds that the individual is engaging in academic dishonety and 'explanations' which explain the reasoning for the confidence score provided, which should be actual text descriptions of how much the inputted image matches up with the criteria. "
            "Do not include any extra text."

        )
    for frame in frames:
        base64_image = encode_image(frame)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    },
                ],
            }
        ]
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.2
            )
            if not response or not response.choices or not response.choices[0].message:
                print("Error processing frame: Invalid response structure.")
                continue

            content = response.choices[0].message.content.strip()
            if not content:
                print("Error processing frame: Empty response content.")
                continue

            try:
                print(content)
                data = json.loads(content)
            except json.JSONDecodeError as json_err:
                print(f"Error processing frame: JSON decode error - {json_err}")
                continue

            for criterion in criteria:
                confidence = data.get("criteria_confidences", {}).get(criterion, 0.0)
                criteria_confidences[criterion].append(confidence)
        except Exception as err:
            print(f"Error processing frame: {err}")
    
    # Calculate average confidence for each criterion
    averaged_confidences = {
        criterion: sum(confidences)/len(confidences) if confidences else 0.0
        for criterion, confidences in criteria_confidences.items()
    }
    
    # Calculate overall probability
    confidences = averaged_confidences.values()
    overall_probability = sum(confidences) / len(confidences) if confidences else 0.0
    
    return {
        "criteria_confidences": averaged_confidences,
        "overall_probability": overall_probability
    }

