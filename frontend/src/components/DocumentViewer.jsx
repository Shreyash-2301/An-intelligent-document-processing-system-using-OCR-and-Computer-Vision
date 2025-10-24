import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Containe          {document.imageUrl && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Document Preview
                </Typography>
                <Box
                  component="img"
                  src={document.imageUrl}
                  sx={{
                    maxWidth: '100%',
                    height: 'auto',
                    display: 'block',
                    margin: '0 auto',
                  }}
                  alt="Document Preview"
                />
              </Paper>
            </Grid>
          )}
        </Grid>graphy,
  Grid,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

const DocumentViewer = () => {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocument();
  }, [id]);

  const fetchDocument = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/documents/${id}`);
      const data = await response.json();
      setDocument(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch document:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!document) {
    return (
      <Typography variant="h6" sx={{ textAlign: 'center', mt: 4 }}>
        Document not found
      </Typography>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Document Details
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Document Information
              </Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>File Name</TableCell>
                      <TableCell>{document.filename}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Upload Date</TableCell>
                      <TableCell>
                        {new Date(document.uploadDate).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>{document.status}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Extracted Data
              </Typography>
              {document.extractedData ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Field</TableCell>
                        <TableCell>Value</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(document.extractedData).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell>{key}</TableCell>
                          <TableCell>{value}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography>No extracted data available</Typography>
              )}
            </Paper>
          </Grid>
          {document.imageUrl && (
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Document Preview
                </Typography>
                <Box
                  component="img"
                  src={document.imageUrl}
                  sx={{
                    maxWidth: '100%',
                    height: 'auto',
                    display: 'block',
                    margin: '0 auto',
                  }}
                  alt="Document Preview"
                />
            </Paper>
          )}
        </Grid>
      </Box>
    </Container>
  );
};

export default DocumentViewer;