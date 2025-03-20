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
    // Create a temporary tab to make the request
    chrome.tabs.create({ url: 'https://sysproctoring.com', active: false }, async (tab) => {
      try {
        // Wait for the tab to load
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Inject a content script to make the request
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          function: makeApiRequest,
          args: [examData]
        });
        
        // Listen for the response from the content script
        const handleResponse = (message, sender) => {
          if (message.action === 'apiResponse' && sender.tab && sender.tab.id === tab.id) {
            // Remove the listener
            chrome.runtime.onMessage.removeListener(handleResponse);
            
            // Close the tab
            chrome.tabs.remove(tab.id);
            
            if (message.success) {
              // Send success response back to the original content script
              sendResponse({
                success: true,
                data: message.data
              });
              
              // Store session information in local storage
              chrome.storage.local.set({
                currentExamSession: {
                  examId: examData.examId,
                  startTime: examData.timestamp,
                  sessionId: message.data.sessionId || null
                }
              });
            } else {
              sendResponse({
                success: false,
                error: message.error
              });
            }
          }
        };
        
        chrome.runtime.onMessage.addListener(handleResponse);
        
        // Set a timeout to close the tab if no response is received
        setTimeout(() => {
          chrome.runtime.onMessage.removeListener(handleResponse);
          chrome.tabs.remove(tab.id);
          sendResponse({
            success: false,
            error: 'Request timed out'
          });
        }, 10000); // 10 seconds timeout
        
      } catch (error) {
        // Close the tab if there's an error
        chrome.tabs.remove(tab.id);
        throw error;
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

// This function will be injected into the temporary tab
function makeApiRequest(examData) {
  // Create the payload
  const payload = {
    examId: examData.examId,
    userId: examData.userId,
    timestamp: examData.timestamp,
    browserInfo: {
      userAgent: navigator.userAgent,
      language: navigator.language
    }
  };
  
  // Make the request from the page context (no CORS issues)
  fetch('/api/exams/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Send the response back to the background script
    chrome.runtime.sendMessage({
      action: 'apiResponse',
      success: true,
      data: data
    });
  })
  .catch(error => {
    // Send the error back to the background script
    chrome.runtime.sendMessage({
      action: 'apiResponse',
      success: false,
      error: error.message
    });
  });
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
