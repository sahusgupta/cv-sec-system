// Check if monitoring is enabled before running the exam detection logic
if (localStorage.getItem('examMonitoring') === 'true') {
    // Wait for the document to be fully loaded before detecting exam
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', detectExamStart);
    } else {
        detectExamStart();
    }
}

function detectExamStart() {
    const currentUrl = window.location.href;
    
    // Check if the current URL matches the expected pattern for starting an exam
    if (currentUrl.includes('/quizzes/') && currentUrl.includes('/take')) {
        notifyExamStarted();
    }
}

function notifyExamStarted() {
    const examId = parseExamIdFromUrl(window.location.href);
    const userId = getUserId(); // Extract user ID dynamically from the page or session

    if (!examId || !userId) {
        console.error("Missing examId or userId. Cannot start exam session.");
        return;
    }

    // Check if extension is properly connected before sending message
    if (!chrome.runtime.id) {
        console.error("Extension context invalidated. Cannot communicate with background script.");
        return;
    }

    // Use chrome.runtime.sendMessage to communicate with the background script
    // to avoid CORS issues with direct fetch from content script
    chrome.runtime.sendMessage({
        action: 'startExam',
        data: {
            examId: examId,
            userId: userId,
            timestamp: Date.now()
        }
    }, response => {
        console.log(response)
        if (response && response.success) {
            console.log('Exam session started:', response.data);
            // You can add any additional functionality here (e.g., showing an alert or notifying the user)
        } else {
            console.error('Error starting exam session:', response ? response.error : 'No response');
        }
    });
}

function parseExamIdFromUrl(url) {
    const parts = url.split('/');
    const quizIndex = parts.indexOf("quizzes");
    if (quizIndex !== -1 && parts[quizIndex + 1]) {
        return parts[quizIndex + 1]; // Return the exam ID (after "quizzes")
    }
    return null; // If no exam ID is found, return null
}

// Dummy function to simulate user ID extraction (replace with actual logic as needed)
function getUserId() {
    // Try to get user ID from Canvas environment variables
    if (window.ENV && window.ENV.current_user_id) {
        return window.ENV.current_user_id;
    }
    
    // Fallback to localStorage if available
    const storedId = localStorage.getItem('userId');
    if (storedId) {
        return storedId;
    }
    
    // Try to extract from page content if available
    const userElement = document.querySelector('meta[name="user_id"]');
    if (userElement && userElement.content) {
        return userElement.content;
    }
    
    // Last resort fallback
    return "unknown_user";
}
