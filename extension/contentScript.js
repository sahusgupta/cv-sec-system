// Check if monitoring is enabled before running the exam detection logic
if (localStorage.getItem('examMonitoring') === 'true') {
    // Wait for the document to be fully loaded before detecting exam
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', detectExamStart);
    } else {
        detectExamStart();
    }
    
    // Listen for messages from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'examStartResult') {
            if (message.success) {
                if (message.isDefault) {
                    console.log('Default exam session started due to timeout:', message.data);
                    // You might want to handle default responses differently
                } else {
                    console.log('Exam session started successfully:', message.data);
                }
                // You can add any additional functionality here (e.g., showing an alert or notifying the user)
            } else {
                console.error('Error starting exam session:', message.error);
            }
        }
    });
}

function detectExamStart() {
    const currentUrl = window.location.href;
    
    // Check for the specific URL you want to target
    const targetUrl = "https://k12.instructure.com/courses/1903726/quizzes/3146054/take";
    
    // Check if the current URL matches the expected pattern for starting an exam
    if (currentUrl.includes('/quizzes/') && currentUrl.includes('/take')) {
        console.log("Exam page detected");
        
        // If it's the specific quiz we're targeting, ensure we send the notification
        if (currentUrl.startsWith(targetUrl)) {
            console.log("Target exam detected, notifying background script");
            notifyExamStarted();
        } else {
            console.log("General exam detected, notifying background script");
            notifyExamStarted();
        }
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

    console.log(`Starting exam notification with examId: ${examId} and userId: ${userId}`);

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
        // This will be called immediately with the acknowledgment
        // The actual result will come later via chrome.runtime.onMessage
        if (response) {
            console.log('Initial response from background script:', response);
        } else {
            console.warn('No initial response from background script, but continuing...');
            // We'll still get a response via the message listener
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
