import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import styles from './App.module.scss';

import { Main } from './Main/Main'


export const App = () => {
  return (
      //<Router basename="/app">
      <Router>
        <Routes>
          <Route path="/" element={<Main />} />
        </Routes>
      </Router>
  );
};

export default App;
