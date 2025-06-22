// Базовые типы для API
export interface Movie {
  id: number;
  title: string;
  title_english?: string;
  release_date: string;
  type: 'movie' | 'tv_show';
  description: string;
  country: string;
  poster_url?: string;
  poster_image?: string;
  avg_rating?: number;
  ratings_count?: number;
  genres: Genre[];
}

export interface Genre {
  id: number;
  name: string;
  movies_count?: number;
}

export interface Review {
  id: number;
  user: string;
  movie: number;
  movie_title?: string;
  rating_value: number;
  comment: string;
  created_at: string;
  is_critic: boolean;
}

export interface Collection {
  id: number;
  name: string;
  description: string;
  movies_count: number;
  is_public: boolean;
  created_at: string;
}

// Типы для API ответов
export interface HomepageData {
  top_movies: Movie[];
  popular_genres: Genre[];
  new_releases: Movie[];
  message?: string;
}

export interface SearchResponse {
  movies: Movie[];
  total_count: number;
  message?: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Типы для компонентов
export interface WidgetProps {
  title: string;
  linkText?: string;
  linkUrl?: string;
}

export interface TopMoviesWidgetProps extends WidgetProps {
  movies: Movie[];
}

export interface PopularGenresWidgetProps extends WidgetProps {
  genres: Genre[];
}

export interface NewReleasesWidgetProps extends WidgetProps {
  movies: Movie[];
}

// Типы для поиска
export interface SearchParams {
  q?: string;
  genre?: string;
  type?: 'movie' | 'tv_show';
  year?: number;
} 