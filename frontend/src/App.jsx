import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import Layout from './components/Layout';
import DocumentViewer from './components/DocumentViewer';
import DocumentUpload from './components/DocumentUpload';
import ProcessingDashboard from './components/ProcessingDashboard';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<ProcessingDashboard />} />
            <Route path="/view/:id" element={<DocumentViewer />} />
            <Route path="/upload" element={<DocumentUpload />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;