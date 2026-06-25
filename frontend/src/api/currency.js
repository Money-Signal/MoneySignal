import axios from 'axios'

const BASE_URL = `${import.meta.env.VITE_API_URL}/api/currency`

export const fetchLatestRates = () => {
  return axios.get(`${BASE_URL}/latest/`)
}

export const fetchChartData = (currencyCode, days = 30) => {
  return axios.get(`${BASE_URL}/history/${currencyCode}/`, {
    params: { days }
  })
}