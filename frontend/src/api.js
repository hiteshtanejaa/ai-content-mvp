import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001' })

export const listCampaigns = () =>
  api.get('/campaigns').then((r) => r.data)

export const createCampaign = (data) =>
  api.post('/campaigns', data).then((r) => r.data)

export const getCampaign = (id) =>
  api.get(`/campaigns/${id}`).then((r) => r.data)

export const updatePost = (campaignId, day, data) =>
  api.patch(`/campaigns/${campaignId}/posts/${day}`, data).then((r) => r.data)

export const regeneratePost = (campaignId, day) =>
  api.post(`/campaigns/${campaignId}/posts/${day}/regenerate`).then((r) => r.data)

export const scheduleAll = (campaignId) =>
  api.post(`/campaigns/${campaignId}/schedule`).then((r) => r.data)
