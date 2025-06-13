# Patient Cohort Simulator

A web application for simulating patient cohorts using aggregated data. The application allows users to generate synthetic patient data based on specified criteria and analyze the resulting cohort.

## Features

- Generate synthetic patient data with customizable parameters
- Age-based clustering of patients
- Statistical analysis of cohort characteristics
- Interactive web interface
- Real-time data visualization

## Tech Stack

- Frontend: React.js
- Backend: FastAPI (Python)
- Data Processing: Pandas, NumPy
- Clustering: Custom age-based clustering algorithm

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pandas numpy scikit-learn
   ```

4. Start the backend server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at http://localhost:3000

## API Documentation

The API documentation is available at http://localhost:8000/docs when the backend server is running.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 