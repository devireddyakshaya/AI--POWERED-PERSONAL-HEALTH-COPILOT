import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AppSettingsProvider } from './context/AppSettings';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AppSettingsProvider>
      <App />
    </AppSettingsProvider>
  </React.StrictMode>
);
