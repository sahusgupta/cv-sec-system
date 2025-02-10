

import openai as oa
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
    import contextlib
    import json
    # Open all frame files in binary mode using an ExitStack to ensure they are properly closed
    with contextlib.ExitStack() as stack:
        file_objs = [stack.enter_context(open(frame, "rb")) for frame in frames]
        
        prompt = (
            "You are a video analysis assistant. Analyze the provided image files. "
            "For each image, determine the confidence that certain specified criteria are met. "
            f"The criteria are: {criteria}. "
            "Return a JSON object with a single key 'criteria_confidences' mapping each criteria to its confidence score (0 to 1). "
            "Do not include any extra text."

        )
        try:
            response = oa.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a video analysis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                files=file_objs  # Pass the opened file objects to GPT4o
            )
            content = response["choices"][0]["message"]["content"]
            data = json.loads(content)
            confidences = list(data.get("criteria_confidences", {}).values())
            overall_probability = sum(confidences) / len(confidences) if confidences else 0.0
            data["overall_probability"] = overall_probability
            return data
        except Exception as err:
            print("Error processing frames:", err)
            return None

