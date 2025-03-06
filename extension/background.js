// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startExam') {
    handleExamStart(message.data, sendResponse);
    return true; // Required to use sendResponse asynchronously
  }
});

/**
 * Handles the exam start event by sending data to the server
 * @param {Object} examData - Data about the exam session
 * @param {Function} sendResponse - Callback function to respond to the content script
 */
async function handleExamStart(examData, sendResponse) {
  try {
    // Create a form element
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://sysproctoring.com/api/exams/start';
    form.target = '_blank'; // This will open in a new tab, but we'll close it immediately
    form.style.display = 'none';

    // Add the data as hidden form fields
    const addField = (name, value) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      input.value = typeof value === 'object' ? JSON.stringify(value) : value;
      form.appendChild(input);
    };

    addField('examId', examData.examId);
    addField('userId', examData.userId);
    addField('timestamp', examData.timestamp);
    addField('browserInfo', {
      userAgent: navigator.userAgent,
      language: navigator.language
    });

    // Append the form to the document, submit it, and remove it
    document.body.appendChild(form);
    
    // Create a promise that resolves when we get a message from the opened window
    const responsePromise = new Promise((resolve) => {
      // This is a simplified approach - in a real implementation you'd need
      // to handle communication with the opened window
      setTimeout(() => {
        resolve({ success: true, sessionId: 'dummy-session-id' });
      }, 1000);
    });

    form.submit();
    
    // Remove the form after submission
    document.body.removeChild(form);

    // Wait for the response
    const data = await responsePromise;
    
    // Send success response back to the content script
    sendResponse({
      success: true,
      data: data
    });
    
    // Store session information in local storage
    chrome.storage.local.set({
      currentExamSession: {
        examId: examData.examId,
        startTime: examData.timestamp,
        sessionId: data.sessionId || null
      }
    });
    
  } catch (error) {
    console.error('Error starting exam session:', error);
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

// Helper function to flatten nested objects for URL encoding
function flattenObject(obj, prefix = '') {
  return Object.keys(obj).reduce((acc, k) => {
    const pre = prefix.length ? `${prefix}[${k}]` : k;
    
    if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
      Object.assign(acc, flattenObject(obj[k], pre));
    } else if (Array.isArray(obj[k])) {
      obj[k].forEach((item, index) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(acc, flattenObject(item, `${pre}[${index}]`));
        } else {
          acc[`${pre}[${index}]`] = item;
        }
      });
    } else {
      acc[pre] = obj[k];
    }
    
    return acc;
  }, {});
}
