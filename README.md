# Transaction Search Project

This project allows you to parse transaction data from PDF files, extract entity names, store the data in MongoDB, and search through the transactions using a web interface.

## Setup and Run Instructions

Follow these steps to set up and run the project:

1. **Download Data**
   Download the transaction data PDF file:
   ```
   wget https://nld.mediacdn.vn/291774122806476800/2024/9/13/danh-sach-ung-ho-1726197796019953464538.pdf -O danh-sach-ung-ho-1726197796019953464538.pdf
   ```
   If you don't have `wget` installed, you can use `curl`:
   ```
   curl -o transactions.pdf https://nld.mediacdn.vn/291774122806476800/2024/9/13/danh-sach-ung-ho-1726197796019953464538.pdf
   ```
   Alternatively, you can manually download the file from the provided URL and save it as `danh-sach-ung-ho-1726197796019953464538.pdf` in the project directory.


1. **Parse Data**
   Run the data parser to convert PDF files to CSV:
   ```
   python data_parser.py
   ```

2. **Extract Names**
   Extract entity names from the transaction descriptions:
   ```
   python extract_name.py
   ```

3. **Insert Data to MongoDB**
   Load the processed data into MongoDB:
   ```
   python insert_db.py
   ```

4. **Setup Backend**
   Install dependencies and start the backend server:
   ```
   cd backend
   npm install
   node server.js
   ```

5. **Setup Frontend**
   Install dependencies and start the frontend development server:
   ```
   cd frontend
   npm install
   npm start
   ```

6. **Access the Application**
   Open your web browser and go to `http://localhost:3000` to use the application.

## Additional Notes

- Ensure MongoDB is installed and running on your local machine.
- Make sure you have Python and Node.js installed.
- You may need to install additional Python packages. Use `pip install -r requirements.txt` if a requirements file is provided.
- The backend runs on port 5000 by default, and the frontend on port 3000.

For more detailed information about each component, refer to the individual script files.