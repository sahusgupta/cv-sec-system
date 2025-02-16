import os
from typing import List
import requests


def get_course_students(course_id: str) -> List[str]:
    """
    Fetch list of students from a Canvas course using the Canvas API
    """
    CANVAS_API_URL = "https://k12.instructure.com"
    CANVAS_TOKEN = "6936~MyKKNTRw4YVhUR6Fv9Ze4FwEhNNAMD3Gk28ET64kFCADm278hZKtwtJcxAGPcCkh"  
    
    if not CANVAS_TOKEN:
        raise ValueError("Canvas token not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {CANVAS_TOKEN}"
    }
    
    endpoint = f"{CANVAS_API_URL}/api/v1/courses/{course_id}/users"

    params = {
        "enrollment_type[]": "student",
        "per_page": 100
    }
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        students = response.json()
        return [student['name'] for student in students]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching students: {str(e)}")
        return []
# Example usage:
if __name__ == "__main__":
    course_id = "1903726"  
    students = get_course_students(course_id)
    print("Students in course:", students)