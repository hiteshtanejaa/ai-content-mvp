import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Campaign from './pages/Campaign'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/campaign/:campaignId" element={<Campaign />} />
      </Routes>
    </BrowserRouter>
  )
}
