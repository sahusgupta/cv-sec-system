(async function() {
    // First, define the SessionLogger class
    class SessionLogger {
        constructor() {
            // Remove the trailing /api since it's already in the routes
            this.API_ENDPOINT = 'http://127.0.0.1:5000';
            this.currentSession = null;
        }

        async startSession(examData) {
            try {
                const response = await fetch(`${this.API_ENDPOINT}/api/sessions/start`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        student_id: examData.userId,
                        exam_id: examData.examId
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                this.currentSession = data.session_id;
                
                // Store session info in chrome storage
                chrome.storage.local.set({
                    currentExamSession: {
                        sessionId: data.session_id,
                        examId: examData.examId,
                        startTime: new Date().toISOString(),
                        status: 'active'
                    }
                });
                
                return data;
            } catch (error) {
                console.error("Error starting session:", error);
                throw error;
            }
        }

        async checkExistingSession(examId, studentId) {
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `${this.API_ENDPOINT}/api/exams/${examId}/sessions?student_id=${studentId}`, true);
                
                xhr.onload = function() {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            resolve(data.activeSession);
                        } catch (e) {
                            resolve(null);
                        }
                    } else {
                        resolve(null);
                    }
                };
                
                xhr.onerror = function() {
                    resolve(null);
                };
                
                xhr.send();
            });
        }

        async logEvent(eventType, eventData) {
            if (!this.currentSession) {
                console.warn("No active session to log events");
                return;
            }
            
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', `${this.API_ENDPOINT}/api/sessions/${this.currentSession}/events`, true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                
                xhr.onload = function() {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            resolve(data);
                        } catch (e) {
                            resolve({status: 'success'});
                        }
                    } else {
                        reject(new Error(`HTTP error! status: ${xhr.status}`));
                    }
                };
                
                xhr.onerror = function() {
                    reject(new Error('Network request failed'));
                };
                
                const payload = JSON.stringify({
                    eventType: eventType,
                    additionalInfo: eventData,
                    timestamp: new Date().toISOString()
                });
                
                xhr.send(payload);
            });
        }

        async endSession() {
            if (!this.currentSession) {
                console.warn("No active session to end");
                return;
            }
            
            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', `${this.API_ENDPOINT}/api/sessions/${this.currentSession}/end`, true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                
                xhr.onload = function() {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        // Clear session from chrome storage
                        chrome.storage.local.remove('currentExamSession');
                        this.currentSession = null;
                        
                        try {
                            const data = JSON.parse(xhr.responseText);
                            resolve(data);
                        } catch (e) {
                            resolve({status: 'success'});
                        }
                    } else {
                        reject(new Error(`HTTP error! status: ${xhr.status}`));
                    }
                }.bind(this);
                
                xhr.onerror = function() {
                    reject(new Error('Network request failed'));
                };
                
                xhr.send();
            });
        }
        
        // Add the missing restoreSession method
        async restoreSession(sessionData) {
            if (sessionData && sessionData.sessionId) {
                this.currentSession = sessionData.sessionId;
                console.log(`Session restored: ${this.currentSession}`);
                return true;
            }
            return false;
        }
    }

    // Create singleton instance
    const sessionLogger = new SessionLogger();

    // Store monitoring listener references for cleanup
    let monitoringListeners = {
        tabActivated: null,
        windowFocus: null,
        tabUpdated: null,
        idleState: null
    };

    function startSessionMonitoring() {
        // Monitor tab changes
        monitoringListeners.tabActivated = async (activeInfo) => {
            try {
                await sessionLogger.logEvent('TAB_SWITCH', {
                    tabId: activeInfo.tabId,
                    windowId: activeInfo.windowId,
                    timestamp: new Date().toISOString()
                });
            } catch (e) {
                console.error("Error logging tab switch:", e);
            }
        };
        chrome.tabs.onActivated.addListener(monitoringListeners.tabActivated);

        // Monitor window focus
        monitoringListeners.windowFocus = async (windowId) => {
            try {
                await sessionLogger.logEvent('WINDOW_FOCUS_CHANGE', {
                    windowId: windowId,
                    hasFocus: windowId !== chrome.windows.WINDOW_ID_NONE,
                    timestamp: new Date().toISOString()
                });
            } catch (e) {
                console.error("Error logging window focus:", e);
            }
        };
        chrome.windows.onFocusChanged.addListener(monitoringListeners.windowFocus);

        // Monitor tab visibility
        monitoringListeners.tabUpdated = async (tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete') {
                try {
                    await sessionLogger.logEvent('TAB_UPDATED', {
                        tabId: tabId,
                        url: tab.url,
                        timestamp: new Date().toISOString()
                    });
                } catch (e) {
                    console.error("Error logging tab update:", e);
                }
            }
        };
        chrome.tabs.onUpdated.addListener(monitoringListeners.tabUpdated);

        // Monitor browser idle state
        monitoringListeners.idleState = async (newState) => {
            try {
                await sessionLogger.logEvent('IDLE_STATE_CHANGE', {
                    state: newState,
                    timestamp: new Date().toISOString()
                });
            } catch (e) {
                console.error("Error logging idle state:", e);
            }
        };
        chrome.idle.onStateChanged.addListener(monitoringListeners.idleState);
    }

    function stopSessionMonitoring() {
        // Remove all monitoring listeners
        if (monitoringListeners.tabActivated) {
            chrome.tabs.onActivated.removeListener(monitoringListeners.tabActivated);
        }
        if (monitoringListeners.windowFocus) {
            chrome.windows.onFocusChanged.removeListener(monitoringListeners.windowFocus);
        }
        if (monitoringListeners.tabUpdated) {
            chrome.tabs.onUpdated.removeListener(monitoringListeners.tabUpdated);
        }
        if (monitoringListeners.idleState) {
            chrome.idle.onStateChanged.removeListener(monitoringListeners.idleState);
        }
        monitoringListeners = {
            tabActivated: null,
            windowFocus: null,
            tabUpdated: null,
            idleState: null
        };
    }

    // Single message listener to handle all extension messages
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        console.log("Background received message:", message);
        
        if (message.action === 'startExam') {
            // Immediately acknowledge receipt
            sendResponse({ received: true, processing: true });
            
            const timeoutId = setTimeout(() => {
                if (sender.tab?.id) {
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
                }
            }, 5000);

            // Start the session
            sessionLogger.startSession(message.data)
                .then(result => {
                    clearTimeout(timeoutId);
                    
                    if (sender.tab?.id) {
                        chrome.tabs.sendMessage(sender.tab.id, {
                            action: 'examStartResult',
                            success: true,
                            data: result
                        });
                    }

                    // Start monitoring automatically after successful session start
                    startSessionMonitoring();
                })
                .catch(error => {
                    clearTimeout(timeoutId);
                    console.error('Error in session start:', error);
                    
                    if (sender.tab?.id) {
                        chrome.tabs.sendMessage(sender.tab.id, {
                            action: 'examStartResult',
                            success: false,
                            error: error.message
                        });
                    }
                });

            return true; // Keep the message channel open for async response
        }
        
        else if (message.action === 'endExam') {
            sessionLogger.endSession()
                .then(() => {
                    sendResponse({ success: true });
                    // Remove all monitoring listeners
                    stopSessionMonitoring();
                })
                .catch(error => {
                    console.error('Error ending session:', error);
                    sendResponse({ success: false, error: error.message });
                });
            return true; // Keep message channel open for async response
        }

        else if (message.action === 'proxyRequest') {
            fetch(message.url, message.options)
                .then(response => response.text())
                .then(data => {
                    sendResponse({
                        status: 200,
                        data: data
                    });
                })
                .catch(error => {
                    sendResponse({
                        error: error.message
                    });
                });
            return true; // Keep the message channel open
        }
    });

    // Automatically restore session on extension reload
    chrome.storage.local.get('currentExamSession', async (data) => {
        if (data.currentExamSession) {
            try {
                const restored = await sessionLogger.restoreSession(data.currentExamSession);
                if (restored) {
                    startSessionMonitoring();
                }
            } catch (error) {
                console.error('Error restoring session:', error);
            }
        }
    });
})();

