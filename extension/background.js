chrome.runtime.onConnect.addListener((port) => {
    port.onMessage.addListener((msg) => {
      if (msg.action === "notifyExamStarted") {
        const { examId, userId } = msg.data;
  
        fetch('http://localhost:3000/api/exams/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            examId: examId,
            userId: userId,
            timestamp: Date.now()
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log('Exam session started:', data);
          port.postMessage({ status: 'success', data });
        })
        .catch(err => {
          console.error('Error:', err);
          port.postMessage({ status: 'error', error: err });
        });
      }
    });
  });
  