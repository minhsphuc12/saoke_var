// Import required modules
const express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');
const dependencies = require('./dependencies');
const morgan = require('morgan');

// Check dependencies
Object.entries(dependencies).forEach(([dep, version]) => {
  try {
    require(dep);
  } catch (error) {
    console.error(`Missing dependency: ${dep}@${version}`);
    process.exit(1);
  }
});

// Initialize Express app
const app = express();
const port = process.env.PORT || 5000;

// Enable CORS and JSON parsing middleware
app.use(cors());
app.use(express.json());

// Configure CORS
const corsOptions = {
  origin: 'http://localhost:3001', // Replace with your frontend URL
  optionsSuccessStatus: 200
};

app.use(cors(corsOptions));

// Add morgan for logging
app.use(morgan('dev'));

// Set up MongoDB connection
const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/transaction_db';
const client = new MongoClient(uri);

// Function to connect to the database
async function connectToDatabase() {
  try {
    await client.connect();
    console.log('Connected to MongoDB');
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
  }
}

// Connect to the database
connectToDatabase();

// API endpoint to fetch transactions
app.get('/api/transactions', async (req, res) => {
  console.log('Received request:', req.method, req.url);
  console.log('Query parameters:', req.query);
  
  // Extract query parameters
  const { search, startDate, endDate, minAmount, maxAmount, page = 1, limit = 10 } = req.query;
  const skip = (page - 1) * limit;

  console.log('Received query params:', { search, startDate, endDate, minAmount, maxAmount, page, limit });

  try {
    // Get the transactions collection
    const collection = client.db('transaction_db').collection('transactions');
    
    // Build the query object based on filters
    let query = {};
    if (search) query.$text = { $search: search };
    if (startDate || endDate) {
      query.trans_date = {};
      if (startDate) query.trans_date.$gte = new Date(startDate);
      if (endDate) query.trans_date.$lte = new Date(endDate);
    }
    if (minAmount || maxAmount) {
      query.credit = {};
      if (minAmount) query.credit.$gte = parseFloat(minAmount);
      if (maxAmount) query.credit.$lte = parseFloat(maxAmount);
    }

    console.log('Constructed query:', JSON.stringify(query, null, 2));

    // Count total matching documents
    const totalCount = await collection.countDocuments(query);

    console.log('Total matching documents:', totalCount);

    // Fetch paginated and sorted transactions
    const transactions = await collection.find(query)
      .sort({ trans_date: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .toArray();

    console.log('Fetched transactions:', transactions.length);

    // Send response
    res.json({
      transactions,
      totalCount,
      currentPage: parseInt(page),
      totalPages: Math.ceil(totalCount / limit)
    });
  } catch (error) {
    // Handle errors
    console.error('Error in /api/transactions:', error);
    res.status(500).json({ message: 'Error fetching transactions', error: error.message });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});