import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import styles from './App.module.scss';

import { Main, apiEndpoint } from './Main/Main'


export const App = () => {
  // backend will redirect / to /app
  let basename = "/app";
  if (apiEndpoint.length > 0) {
    basename = "";
  }
  return (
      <Router basename={`${basename}`}>
        <Routes>
          <Route path="/" element={<Main />} />
        </Routes>
      </Router>
  );
};

export default App;
