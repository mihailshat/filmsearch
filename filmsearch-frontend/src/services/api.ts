import axios, { AxiosResponse } from 'axios';
import { HomepageData, SearchResponse, Movie, SearchParams } from '../types/api';

// Базовый URL для API
const API_BASE_URL = 'http://localhost:8000/api';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API функции для главной страницы
export const homepageAPI = {
  // Получить данные для всех виджетов главной страницы
  getHomepageData: (): Promise<AxiosResponse<HomepageData>> => 
    api.get<HomepageData>('/homepage/'),
  
  // Поиск фильмов
  searchMovies: (params: SearchParams): Promise<AxiosResponse<SearchResponse>> => 
    api.get<SearchResponse>('/search/', { params }),
  
  // Детальная информация о фильме
  getMovieDetail: (movieId: number): Promise<AxiosResponse<Movie>> => 
    api.get<Movie>(`/movie/${movieId}/`),
};

// Обработка ошибок
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Более детальная обработка ошибок
    if (error.response) {
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Request error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api; 