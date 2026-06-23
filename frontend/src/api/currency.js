import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000/api/currency'

export const fetchLatestRates = () => {
  return axios.get(`${BASE_URL}/latest/`)
}

export const fetchChartData = (currencyCode, days = 30) => {
  return axios.get(`${BASE_URL}/history/${currencyCode}/`, {
    params: { days }
  })
}