// Check if monitoring is enabled before running the exam detection logic
if (localStorage.getItem('examMonitoring') === 'true') {
    detectExamStart();
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

    fetch('https://www.sysproctoring.com/api/exams/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            examId: examId,
            userId: userId,
            timestamp: Date.now(),
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to start exam session: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Exam session started:', data);
        // You can add any additional functionality here (e.g., showing an alert or notifying the user)
    })
    .catch(err => {
        console.error('Error starting exam session:', err);
    });
}

function parseExamIdFromUrl(url) {
    const parts = url.split('/');
    if (quizIndex !== -1 && parts[quizIndex + 1]) {
        return parts[quizIndex + 1]; // Return the exam ID (after "quizzes")
    }
    return null; // If no exam ID is found, return null
}

// Dummy function to simulate user ID extraction (replace with actual logic as needed)
function getUserId() {
    // This is just a placeholder. Ideally, you would extract the user ID dynamically from the page
    // For example, from a global JavaScript variable or from the logged-in user info in localStorage.
    return localStorage.getItem('userId') || "defaultUserId";
}
