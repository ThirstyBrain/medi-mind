import React, { useState } from 'react';
import { TextField, Button, Typography, Container, Paper, CircularProgress, Box } from '@mui/material';
import axios from 'axios';

const Chatbot: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!question) {
      setAnswer('Please enter a question.');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/api/ask/',
        { question },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setAnswer(response.data.answer);
    } catch (error: any) {
      console.error('API Error:', error.response?.data || error.message);
      setAnswer(`Error: ${error.response?.data?.error || 'Something went wrong.'}`);
    }
    setLoading(false);
  };

  // Split the answer into paragraphs and render them
  const renderAnswer = (text: string) => {
    const paragraphs = text.split('\n\n').filter((p) => p.trim() !== '');
    return paragraphs.map((paragraph, index) => (
      <Typography
        key={index}
        variant="body1"
        sx={{
          marginBottom: '1rem',
          lineHeight: 1.6,
          color: '#333',
          textAlign: 'justify',
        }}
      >
        {paragraph}
      </Typography>
    ));
  };

  return (
    <Container maxWidth="md" sx={{ marginTop: '2rem', marginBottom: '2rem' }}>
      <Paper
        elevation={3}
        sx={{
          padding: '2rem',
          borderRadius: '12px',
          backgroundColor: '#fff',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Typography
          variant="h4"
          gutterBottom
          sx={{ fontWeight: 600, color: '#1976d2', textAlign: 'center' }}
        >
          Healthcare Chatbot
        </Typography>
        <TextField
          label="Ask a healthcare question"
          variant="outlined"
          fullWidth
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          sx={{ marginBottom: '1.5rem', backgroundColor: '#f9f9f9' }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={loading}
          sx={{ padding: '0.75rem 2rem', fontSize: '1rem', borderRadius: '8px' }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : 'Ask'}
        </Button>
        {answer && (
          <Box
            sx={{
              marginTop: '2rem',
              padding: '1.5rem',
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              borderLeft: '4px solid #1976d2',
            }}
          >
            <Typography
              variant="h6"
              sx={{ fontWeight: 500, color: '#1976d2', marginBottom: '1rem' }}
            >
              Answer
            </Typography>
            {renderAnswer(answer)}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Chatbot;