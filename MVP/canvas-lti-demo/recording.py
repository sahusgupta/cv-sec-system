import os
from typing import List
import requests


def get_course_students(course_id: str) -> List[str]:

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


def get_quiz_progress():
    API_BASE_URL = "https://k12.instructure.com/api/v1"
    ACCESS_TOKEN = "6936~MyKKNTRw4YVhUR6Fv9Ze4FwEhNNAMD3Gk28ET64kFCADm278hZKtwtJcxAGPcCkh"
    COURSE_ID = 1903726
    QUIZ_ID = 3146054 
    STUDENT_ID = 11367013

    # Request the quiz submission for the specific student
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = f"{API_BASE_URL}/courses/{COURSE_ID}/quizzes/{QUIZ_ID}/submissions?user_id={STUDENT_ID}"

    response = requests.get(url, headers=headers)
    data = response.json()


    a = requests.get(f"https://k12.instructure.com/api/v1/courses/{COURSE_ID}/external_tools", headers=headers)
    print(str(a.json()) + "/ hi my name jeff")
    # Parse the response
    if "quiz_submissions" in data and len(data["quiz_submissions"]) > 0:
        submission = data["quiz_submissions"][0]
        print(f"Student {STUDENT_ID} Quiz Status: {submission['workflow_state']}")
    else:
        print("No quiz submission found for this student.")

# Example usage:
if __name__ == "__main__":
    course_id = "1903726"  
    students = get_course_students(course_id)
    print("Students in course:", students)
    get_quiz_progress()