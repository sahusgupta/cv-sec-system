import os
import requests
import json
import threading
import time
import pyautogui as pag
import cv2
import numpy as np
import keyboard
import screeninfo
import pyperclip
import pygetwindow as gw
from canvasapi import Canvas

class CanvasProctor:
    def __init__(self, canvas_url, api_key, course_id, assignment_id):
        self.canvas = Canvas(canvas_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.assignment = self.course.get_assignment(assignment_id)
        
        self.last_clipboard_content = pyperclip.paste()
        self.monitoring = False
        self.screenshot_interval = 60  
        self.last_screenshot_time = 0
        self.out = "log.txt"
        self.compliance_issues = []
        self.is_exam_active = False
        self.active_window = gw.getActiveWindow().title if gw.getActiveWindow() else "Unknown"

    def log(self, event, severity='INFO'):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} [{severity}]: {event}\n"
        with open(self.out, "a") as f:
            f.write(log_entry)
        if severity == 'CRITICAL':
            self._report_compliance_issue(event)

    def _report_compliance_issue(self, issue_description):
        try:
            submission = self.assignment.get_submission(self.student.id)
            submission.create_submission_comment(comment=f"Proctoring Violation: {issue_description}")
        except Exception as e:
            self.log(f"Failed to report compliance issue: {str(e)}", 'WARN')

    def validate_exam_environment(self):
        checks = [
            self._check_single_display(),
            self._check_allowed_applications(),
            self._verify_student_identity()
        ]
        
        return all(checks)

    def _check_single_display(self):
        is_single_display = len(screeninfo.get_monitors()) == 1
        if not is_single_display:
            self.log("Multiple displays detected", 'CRITICAL')
        return is_single_display

    def _check_allowed_applications(self):
        return True

    def _verify_student_identity(self):
        return True

    def _focus_monitor(self):
        while self.monitoring and self.is_exam_active:
            current_window = gw.getActiveWindow().title if gw.getActiveWindow() else "Unknown"
            if current_window != self.active_window:
                self.log(f"Focus changed! User switched to: {current_window}", 'CRITICAL')
                self.active_window = current_window
            time.sleep(1)

    def start_exam_monitoring(self, student):
        self.student = student
        
        if not self.validate_exam_environment():
            self.log("Exam environment non-compliant", 'CRITICAL')
            return False
            
        self.is_exam_active = True
        self.monitoring = True
        
        import random
        def frame_analysis_thread():
            from MVP.process import process_frames
            import glob, time
            processed_frames = set()
            while self.monitoring and self.is_exam_active:
                frames = sorted(glob.glob("exam_screenshot_*.png"))
                new_frames = [f for f in frames if f not in processed_frames]
                threshold = random.randint(10, 15)
                if len(new_frames) >= threshold:
                    frames_to_analyze = new_frames[:threshold]
                    result = process_frames(frames_to_analyze, criteria="Device present in camera, Multiple people present in frame, Inconsistent gaze position, turning head, frequently glancing down at lap")
                    
                    self.log(f"Analyzed {len(frames_to_analyze)} frames, analysis result: {result}", 'INFO')
                    processed_frames.update(frames_to_analyze)
                time.sleep(2)
        
        threads = [
            threading.Thread(target=self._clipboard_monitor),
            threading.Thread(target=self._screenshot_monitor),
            threading.Thread(target=self._hotkey_monitor),
            threading.Thread(target=self._focus_monitor),
            threading.Thread(target=frame_analysis_thread)
        ]
        
        for thread in threads:
            thread.start()
        
        return True

    def _clipboard_monitor(self):
        while self.monitoring and self.is_exam_active:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard_content:
                    self.log(f"Clipboard change detected: {current_clipboard}", 'WARN')
                    self.last_clipboard_content = current_clipboard
                time.sleep(0.5)
            except Exception as e:
                self.log(f"Clipboard monitoring error: {str(e)}", 'WARN')

    def _screenshot_monitor(self):
        while self.monitoring and self.is_exam_active:
            current_time = time.time()
            if current_time - self.last_screenshot_time >= self.screenshot_interval:
                screenshot = pag.screenshot()
                screenshot_filename = f"exam_screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(screenshot_filename)
                
                self._analyze_screenshot(screenshot_filename)
                
                self.log(f"Screenshot captured: {screenshot_filename}")
                self.last_screenshot_time = current_time
            
            time.sleep(1)

    def _analyze_screenshot(self, screenshot_path):
        pass

    def _hotkey_monitor(self):
        keyboard.add_hotkey('ctrl+c', lambda: self.log('CTRL + C Intercepted', 'WARN'), suppress=True)
        keyboard.add_hotkey('ctrl+v', lambda: self.log('CTRL + V Intercepted', 'WARN'), suppress=True)
        keyboard.add_hotkey('ctrl+n', lambda: self.log('CTRL + N Intercepted', 'WARN'), suppress=True)

    def end_exam(self):
        self.is_exam_active = False
        self.monitoring = False
        self._submit_exam_report()

    def _submit_exam_report(self):
        report = {
            'student_id': self.student.id,
            'assignment_id': self.assignment.id,
            'compliance_issues': self.compliance_issues,
            'log_file': self.out
        }
        try:
            submission = self.assignment.get_submission(self.student.id)
            submission.edit(submission={'extra_submissions': json.dumps(report)})
        except Exception as e:
            self.log(f"Failed to submit exam report: {str(e)}", 'WARN')

def main():
    CANVAS_URL = os.environ.get('CANVAS_URL', 'https://katyisd.instructure.com')
    API_KEY = '6936~ta67BQcPu8JuMa3MRnRnYTPJX6HW4E3A2DWNrf3XaztNtLQUEYmtxRktZ9QmK23D'
    COURSE_ID = 12345 
    ASSIGNMENT_ID = 67890
    
    proctor = CanvasProctor(CANVAS_URL, API_KEY, COURSE_ID, ASSIGNMENT_ID)
    
    student = proctor.canvas.get_user("k1412229")
    if proctor.start_exam_monitoring(student):
        pass

if __name__ == "__main__":
    main()