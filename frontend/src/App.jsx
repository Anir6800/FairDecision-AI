import { BrowserRouter, Route, Routes } from 'react-router-dom'

import ErrorBoundary from './components/ErrorBoundary.jsx'
import BiasAudit from './pages/BiasAudit.jsx'
import Explanation from './pages/Explanation.jsx'
import Processing from './pages/Processing.jsx'
import Results from './pages/Results.jsx'
import Upload from './pages/Upload.jsx'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/processing" element={<Processing />} />
          <Route path="/results/:evaluationId" element={<Results />} />
          <Route path="/results/:evaluationId/bias" element={<BiasAudit />} />
          <Route path="/results/:evaluationId/explanation" element={<Explanation />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
