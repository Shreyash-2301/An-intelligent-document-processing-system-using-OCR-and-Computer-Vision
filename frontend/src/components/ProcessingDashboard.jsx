import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  LinearProgress,
} from '@mui/material';
import { Visibility, Download } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const ProcessingDashboard = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/documents');
      const data = await response.json();
      setDocuments(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setLoading(false);
    }
  };

  const handleView = (id) => {
    navigate(`/view/${id}`);
  };

  const handleDownload = async (id, filename) => {
    try {
      const response = await fetch(`http://localhost:8000/api/documents/${id}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Document Processing Dashboard
        </Typography>
        <Grid container spacing={3}>
          {documents.map((doc) => (
            <Grid item xs={12} sm={6} md={4} key={doc.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" noWrap>
                    {doc.filename}
                  </Typography>
                  <Typography color="textSecondary">
                    Status: {doc.status}
                  </Typography>
                  <Typography variant="body2">
                    Uploaded: {new Date(doc.uploadDate).toLocaleDateString()}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => handleView(doc.id)}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Download />}
                    onClick={() => handleDownload(doc.id, doc.filename)}
                  >
                    Download
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default ProcessingDashboard;