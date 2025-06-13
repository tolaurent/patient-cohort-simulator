import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

function App() {
  const [criteria, setCriteria] = useState({
    age_mean: 50,
    age_std: 15,
    glucose_mean: 100,
    glucose_std: 20,
    cholesterol_mean: 200,
    cholesterol_std: 40,
    conditions: ['Diabetes', 'Hypertension', 'Asthma', 'Arthritis'],
    medications: ['Metformin', 'Lisinopril', 'Albuterol', 'Ibuprofen'],
  });
  const [cohortSize, setCohortSize] = useState(100);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      console.log('Sending request to backend...');
      const response = await fetch(`${API_URL}/simulate-cohort`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          criteria: {
            age_mean: parseFloat(criteria.age_mean),
            age_std: parseFloat(criteria.age_std),
            glucose_mean: parseFloat(criteria.glucose_mean),
            glucose_std: parseFloat(criteria.glucose_std),
            cholesterol_mean: parseFloat(criteria.cholesterol_mean),
            cholesterol_std: parseFloat(criteria.cholesterol_std),
            conditions: criteria.conditions.map(c => c.trim()).filter(Boolean),
            medications: criteria.medications.map(m => m.trim()).filter(Boolean)
          },
          size: parseInt(cohortSize)
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      console.log('Received response from backend');

      const data = await response.json();
      console.log('Parsed response data:', data);
      
      if (!response.ok) {
        let errorMessage = 'An error occurred while simulating the cohort.';
        if (data.detail) {
          if (typeof data.detail === 'string') {
            errorMessage = data.detail;
          } else if (data.detail.detail) {
            errorMessage = data.detail.detail;
            if (data.detail.traceback) {
              console.error('Error traceback:', data.detail.traceback);
            }
          }
        }
        throw new Error(errorMessage);
      }

      setResults(data);
    } catch (error) {
      let errorMessage = 'An error occurred while simulating the cohort.';
      if (error.name === 'AbortError') {
        errorMessage = 'Request timed out after 30 seconds. The server might be processing a large cohort. Please try again with a smaller cohort size.';
      } else if (error.message === 'Failed to fetch') {
        errorMessage = 'Could not connect to the server. Please ensure the backend is running at http://localhost:8000';
      } else {
        errorMessage = error.message;
      }
      setError(errorMessage);
      console.error('Error details:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderResults = () => {
    if (!results || !results.summary) return null;

    const conditionData = Object.entries(results.summary.condition_frequency || {}).map(
      ([name, value]) => ({ name, value })
    );

    const medicationData = Object.entries(results.summary.medication_frequency || {}).map(
      ([name, value]) => ({ name, value })
    );

    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Cohort Summary
          </Typography>
          <Card>
            <CardContent>
              <Typography>
                Total Patients: {results.summary.total_patients}
              </Typography>
              <Typography>
                Average Age: {results.summary.age_stats?.mean?.toFixed(1) || 'N/A'} years
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {conditionData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Condition Distribution
            </Typography>
            <PieChart width={400} height={300}>
              <Pie
                data={conditionData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {conditionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </Grid>
        )}

        {medicationData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Medication Distribution
            </Typography>
            <BarChart width={400} height={300} data={medicationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </Grid>
        )}
      </Grid>
    );
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Patient Cohort Simulator
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Age Mean"
                type="number"
                value={criteria.age_mean}
                onChange={(e) =>
                  setCriteria({ ...criteria, age_mean: Number(e.target.value) })
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Age Standard Deviation"
                type="number"
                value={criteria.age_std}
                onChange={(e) =>
                  setCriteria({ ...criteria, age_std: Number(e.target.value) })
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Glucose Mean"
                type="number"
                value={criteria.glucose_mean}
                onChange={(e) =>
                  setCriteria({ ...criteria, glucose_mean: Number(e.target.value) })
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Glucose Standard Deviation"
                type="number"
                value={criteria.glucose_std}
                onChange={(e) =>
                  setCriteria({ ...criteria, glucose_std: Number(e.target.value) })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Cohort Size"
                type="number"
                value={cohortSize}
                onChange={(e) => setCohortSize(Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSimulate}
                fullWidth
                disabled={loading}
              >
                {loading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} />
                    Simulating...
                  </>
                ) : (
                  'Simulate Cohort'
                )}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {renderResults()}
      </Box>
    </Container>
  );
}

export default App;
