let cameraStream = null;

// Initialize camera preview with more robust error handling
async function setupCamera() {
    const cameraStatus = document.getElementById('cameraStatus');
    const permissionsWarning = document.getElementById('permissionsWarning');
    const videoElement = document.getElementById('cameraPreview');

    try {
        cameraStatus.textContent = 'Requesting camera access...';
        
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });

        cameraStream = stream;
        videoElement.srcObject = stream;
        
        // Add event listeners to verify video is playing
        videoElement.onloadedmetadata = () => {
            cameraStatus.textContent = 'Camera loaded, starting preview...';
            videoElement.play()
                .then(() => {
                    cameraStatus.textContent = 'Camera preview active';
                    permissionsWarning.style.display = 'none';
                })
                .catch(err => {
                    cameraStatus.textContent = `Error playing video: ${err.message}`;
                    permissionsWarning.style.display = 'block';
                });
        };

        // Verify stream is active
        if (stream.active) {
            const videoTrack = stream.getVideoTracks()[0];
            if (videoTrack) {
                cameraStatus.textContent += `\nVideo track: ${videoTrack.label}`;
            }
        } else {
            cameraStatus.textContent = 'Stream not active';
            permissionsWarning.style.display = 'block';
        }

    } catch (err) {
        console.error('Camera setup error:', err);
        cameraStatus.textContent = `Camera error: ${err.message}`;
        permissionsWarning.style.display = 'block';
    }
}

// Listen for messages from the background script about exam status
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'examStatus') {
        updateExamStatus(message.data);
    }
});

function updateExamStatus(examData) {
    const statusContainer = document.getElementById('examStatus');
    const examInfo = document.getElementById('examInfo');

    if (examData.isActive) {
        statusContainer.className = 'status-container status-active';
        statusContainer.innerHTML = '<strong>Exam in Progress</strong>';
        
        examInfo.style.display = 'block';
        document.getElementById('examName').textContent = examData.name || 'Untitled Quiz';
        document.getElementById('examDuration').textContent = `Time remaining: ${examData.timeRemaining || 'N/A'}`;
    } else {
        statusContainer.className = 'status-container status-inactive';
        statusContainer.innerHTML = '<strong>No active exam detected</strong>';
        examInfo.style.display = 'none';
    }
}

// Initialize the extension
document.addEventListener('DOMContentLoaded', () => {
    setupCamera();
});

// Add cleanup for camera when window closes
window.addEventListener('unload', () => {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
    }
});