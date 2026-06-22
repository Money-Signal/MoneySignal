import apiClient from './axios'

export const signup        = (data) => apiClient.post('/accounts/signup/', data)
export const login         = (data) => apiClient.post('/accounts/login/', data)
export const logout        = ()     => apiClient.post('/accounts/logout/')
export const refresh       = (data) => apiClient.post('/accounts/token/refresh/', data)
export const getProfile    = ()     => apiClient.get('/accounts/me/')
export const updateProfile = (data) => apiClient.patch('/accounts/me/', data, { headers: { 'Content-Type': 'multipart/form-data' } })
export const deleteAccount = ()     => apiClient.delete('/accounts/me/')
