require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const admin = require('firebase-admin');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Firebase Admin SDK Initialization
// Ensure your Firebase Admin SDK JSON file is correctly configured
try {
  const serviceAccount = require('./firebase-admin-sdk.json');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
  console.log('Firebase Admin SDK initialized successfully.');
} catch (error) {
  console.error('Error initializing Firebase Admin SDK:', error.message);
  console.warn('Please ensure firebase-admin-sdk.json exists and is valid.');
}

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Basic Route
app.get('/', (req, res) => {
  res.send('Compliance Tracker Backend API');
});

// Import Routes (will be added later)
// const complianceRoutes = require('./routes/compliance.routes');
// app.use('/api/compliance', complianceRoutes);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
