import React, { useState, useEffect } from 'react';

function App() {
  const [tabInfo, setTabInfo] = useState<chrome.tabs.Tab | null>(null);
  const [savedData, setSavedData] = useState<{url: string, timestamp: string} | null>(null);

  useEffect(() => {
    // Ensure chrome APIs are available
    if (chrome?.tabs && chrome?.storage) {
      // Get current active tab information
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        setTabInfo(tabs[0]);
      });

      // Retrieve saved data from chrome storage
      chrome.storage.sync.get(['extensionData'], (result) => {
        setSavedData(result.extensionData || null);
      });
    }
  }, []);

  const handleSaveData = () => {
    if (tabInfo && chrome?.storage) {
      const dataToSave = {
        url: tabInfo.url || '',
        timestamp: new Date().toISOString()
      };

      chrome.storage.sync.set({ extensionData: dataToSave }, () => {
        setSavedData(dataToSave);
      });
    }
  };

  const handleSendMessage = () => {
    if (tabInfo && chrome?.tabs) {
      chrome.tabs.sendMessage(tabInfo.id!, { 
        action: 'processPage', 
        url: tabInfo.url 
      });
    }
  };

  return (
    <div className="popup-container">
      <h1>Chrome Extension</h1>
      
      {tabInfo && (
        <div className="tab-info">
          <p>Current Site: {tabInfo.url}</p>
        </div>
      )}

      <div className="actions">
        <button onClick={handleSaveData}>Save Current Site</button>
        <button onClick={handleSendMessage}>Process Page</button>
      </div>

      {savedData && (
        <div className="saved-data">
          <h2>Last Saved:</h2>
          <p>URL: {savedData.url}</p>
          <p>Timestamp: {savedData.timestamp}</p>
        </div>
      )}
    </div>
  );
}

export default App;