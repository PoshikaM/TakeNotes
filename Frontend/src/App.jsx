import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Notes from './pages/Notes';
import { Toaster } from 'react-hot-toast';
import { useState } from 'react';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Toaster />
        <Routes>
          <Route path="/signup" element={<Signup />} />
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/notes" element={token ? <Notes token={token} /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;