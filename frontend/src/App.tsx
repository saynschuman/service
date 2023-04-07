import { Fragment } from 'react';
import { BrowserRouter } from 'react-router-dom';

import CssBaseline from '@mui/material/CssBaseline';

import { withErrorHandler } from '@/error-handling';
import AppErrorBoundaryFallback from '@/error-handling/fallbacks/App';
import Notifications from '@/sections/Notifications';
import SW from '@/sections/SW';

import './style.css';

function App() {

  return (
    <Fragment>
      <CssBaseline />
      <Notifications />
      <SW />

      <BrowserRouter>
        <>hello</>
      </BrowserRouter>
    </Fragment>
  );
}

export default withErrorHandler(App, AppErrorBoundaryFallback);
