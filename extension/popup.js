document.getElementById('startMonitoring').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            function: enableMonitoring
        });
    });
    document.getElementById('status').textContent = "Status: Monitoring Active";
    document.getElementById('startMonitoring').disabled = true;
    document.getElementById('stopMonitoring').disabled = false;
});

document.getElementById('stopMonitoring').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            function: disableMonitoring
        });
    });
    document.getElementById('status').textContent = "Status: Not Monitoring";
    document.getElementById('startMonitoring').disabled = false;
    document.getElementById('stopMonitoring').disabled = true;
});

function enableMonitoring() {
    localStorage.setItem('examMonitoring', 'true');
    console.log("Monitoring Enabled");
}

function disableMonitoring() {
    localStorage.setItem('examMonitoring', 'false');
    console.log("Monitoring Disabled");
}
