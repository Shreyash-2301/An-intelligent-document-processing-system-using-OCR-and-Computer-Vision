import { useState } from 'react';
import { Box, Container, Paper, Typography, Button } from '@mui/material';
import { UploadFile } from '@mui/icons-material';

const DocumentUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      console.log('Upload successful:', data);
      // Handle success (e.g., show notification, redirect)
    } catch (error) {
      console.error('Upload failed:', error);
      // Handle error
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Upload Document
          </Typography>
          <Box
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              p: 3,
              textAlign: 'center',
              mb: 2,
            }}
          >
            <input
              accept="image/*,.pdf,.doc,.docx"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileSelect}
            />
            <label htmlFor="file-upload">
              <Button
                component="span"
                variant="contained"
                startIcon={<UploadFile />}
              >
                Select File
              </Button>
            </label>
            {selectedFile && (
              <Typography sx={{ mt: 2 }}>
                Selected: {selectedFile.name}
              </Typography>
            )}
          </Box>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            disabled={!selectedFile}
            onClick={handleUpload}
          >
            Upload and Process
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default DocumentUpload;