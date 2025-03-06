// Check if monitoring is enabled before running the exam detection logic
if (localStorage.getItem('examMonitoring') === 'true') {
    detectExamStart();
}

function detectExamStart() {
    const currentUrl = window.location.href;
    if (currentUrl.includes('/quizzes/') && currentUrl.includes('/take')) {
        notifyExamStarted();
    }
}

function notifyExamStarted() {
    const examId = parseExamIdFromUrl(window.location.href);
    const userId = "placeholderUser"; // Replace with logic to extract user ID if possible

    fetch('http://localhost:3000/api/exams/start', {  // Make request to your own backend
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            examId: examId,
            userId: userId,
            timestamp: Date.now(),
        })
    })
    .then(response => response.json())
    .then(data => console.log('Exam session started:', data))
    .catch(err => console.error('Error:', err));
}

function parseExamIdFromUrl(url) {
    const parts = url.split('/');
    const quizIndex = parts.indexOf('quizzes');
    return quizIndex !== -1 && parts[quizIndex + 1] ? parts[quizIndex + 1] : null;
}
