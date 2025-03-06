const express = require('express');
const fetch = require('node-fetch');
const app = express();

// Middleware to parse JSON bodies
app.use(express.json());

// Route to handle the proxy request
app.post('/api/exams/start', async (req, res) => {
  try {
    // Forward the request to the SysProctoring API
    const response = await fetch('https://www.sysproctoring.com/api/exams/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body), // Forward the body from the frontend
    });

    if (!response.ok) {
      return res.status(500).json({ error: 'Failed to start exam session' });
    }

    const data = await response.json(); // Get response from SysProctoring API

    // Send the response from SysProctoring back to the frontend
    res.json(data);
  } catch (error) {
    console.error('Error starting exam session:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Start the server on port 3000
app.listen(3000, () => {
  console.log('Server is running on http://localhost:3000');
});
