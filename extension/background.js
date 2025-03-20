// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'startExam') {
    // Immediately acknowledge receipt of the message
    // This keeps the message channel open
    sendResponse({ received: true, processing: true });
    
    // Set a timeout to send a default response if the API calls take too long
    const timeoutId = setTimeout(() => {
      if (sender.tab && sender.tab.id) {
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'examStartResult',
          success: true,
          data: {
            sessionId: `default-session-${Date.now()}`,
            status: "pending",
            message: "Default response due to timeout"
          },
          isDefault: true
        });
        
        // Store default session information in local storage
        chrome.storage.local.set({
          currentExamSession: {
            examId: message.data.examId,
            startTime: message.data.timestamp,
            sessionId: `default-session-${Date.now()}`,
            isDefault: true
          }
        });
        
        console.log("Sent default response due to timeout");
      }
    }, 5000); // 5 seconds timeout
    
    // Then handle the exam start in a separate function
    handleExamStart(message.data)
      .then(result => {
        // Cancel the timeout since we got a real response
        clearTimeout(timeoutId);
        
        // We'll use a different method to send the result back
        // since the original sendResponse channel may be closed
        if (sender.tab && sender.tab.id) {
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'examStartResult',
            success: true,
            data: result
          });
        }
      })
      .catch(error => {
        // Cancel the timeout since we got a real (error) response
        clearTimeout(timeoutId);
        
        console.error('Error in handleExamStart:', error);
        if (sender.tab && sender.tab.id) {
          chrome.tabs.sendMessage(sender.tab.id, {
            action: 'examStartResult',
            success: false,
            error: error.message
          });
        }
      });
    
    // Return false since we've already responded
    return false;
  }
});

/**
 * Handles the exam start event by sending data to the server
 * @param {Object} examData - Data about the exam session
 * @returns {Promise<Object>} - Promise that resolves with the API response data
 */
async function handleExamStart(examData) {
  console.log("Handling exam start", examData);
  
  // Prepare the data to be sent to the server
  const payload = {
    examId: examData.examId,
    userId: examData.userId,
    timestamp: examData.timestamp,
    browserInfo: {
      userAgent: navigator.userAgent,
      language: navigator.language
    }
  };

  console.log("Sending payload to API:", payload);

  // First attempt: Direct fetch with JSON
  try {
    const response = await fetch('https://sysproctoring.com/api/exams/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    console.log("API response status:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("API response data:", data);
      
      // Store session information in local storage
      chrome.storage.local.set({
        currentExamSession: {
          examId: examData.examId,
          startTime: examData.timestamp,
          sessionId: data.sessionId || null
        }
      });
      
      return data;
    }
  } catch (directFetchError) {
    console.error("Direct fetch failed:", directFetchError);
    // Continue to second attempt
  }

  // Second attempt: Form-encoded data
  try {
    console.log("Trying form-encoded approach");
    
    const formData = new URLSearchParams();
    for (const [key, value] of Object.entries(flattenObject(payload))) {
      formData.append(key, value);
    }
    
    const response = await fetch('https://sysproctoring.com/api/exams/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    });

    console.log("Form-encoded API response status:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("Form-encoded API response data:", data);
      
      // Store session information in local storage
      chrome.storage.local.set({
        currentExamSession: {
          examId: examData.examId,
          startTime: examData.timestamp,
          sessionId: data.sessionId || null
        }
      });
      
      return data;
    }
  } catch (formFetchError) {
    console.error("Form-encoded fetch failed:", formFetchError);
    // Continue to final attempt
  }

  // Final attempt: No-cors mode as a last resort
  console.log("Trying no-cors mode as final attempt");
  
  try {
    await fetch('https://sysproctoring.com/api/exams/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      mode: 'no-cors'
    });
    
    // Since we don't get a response with no-cors mode, create a dummy one
    const dummyResponse = {
      sessionId: `session-${Date.now()}`,
      status: "pending",
      message: "Request sent in no-cors mode, actual status unknown"
    };
    
    // Store session information in local storage
    chrome.storage.local.set({
      currentExamSession: {
        examId: examData.examId,
        startTime: examData.timestamp,
        sessionId: dummyResponse.sessionId,
        isFailover: true
      }
    });
    
    return dummyResponse;
  } catch (noCorsError) {
    console.error("No-cors fetch also failed:", noCorsError);
    throw new Error("All API request methods failed");
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
