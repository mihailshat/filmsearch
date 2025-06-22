import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert, Spinner } from 'react-bootstrap';
import TopMoviesWidget from './widgets/TopMoviesWidget';
import PopularGenresWidget from './widgets/PopularGenresWidget';
import NewReleasesWidget from './widgets/NewReleasesWidget';
import Header from './common/Header';
import Footer from './common/Footer';
import { homepageAPI } from '../services/api';
import { HomepageData } from '../types/api';

const HomePage: React.FC = () => {
  const [data, setData] = useState<HomepageData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHomepageData();
  }, []);

  const fetchHomepageData = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await homepageAPI.getHomepageData();
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки данных. Проверьте подключение к серверу.');
      console.error('Error fetching homepage data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Загрузка...</span>
        </Spinner>
        <p className="mt-3">Загрузка данных...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <Alert.Heading>Ошибка загрузки</Alert.Heading>
          <p>{error}</p>
          <button 
            className="btn btn-outline-danger" 
            onClick={fetchHomepageData}
          >
            Попробовать снова
          </button>
        </Alert>
      </Container>
    );
  }

  return (
    <div className="homepage">
      {/* Header с навигацией и hero-секцией */}
      <Header />

      <Container>
        {/* Виджеты главной страницы */}
        <Row>
          {/* Топ фильмов по рейтингу */}
          <Col lg={6} className="mb-4">
            <TopMoviesWidget 
              title="🏆 Топ фильмов по рейтингу"
              movies={data?.top_movies || []} 
              linkText="Смотреть все топ-фильмы"
              linkUrl="/top-movies"
            />
          </Col>

          {/* Популярные жанры */}
          <Col lg={6} className="mb-4">
            <PopularGenresWidget 
              title="📊 Популярные жанры"
              genres={data?.popular_genres || []} 
              linkText="Все жанры"
              linkUrl="/genres"
            />
          </Col>
        </Row>

        <Row>
          {/* Новинки */}
          <Col lg={12} className="mb-4">
            <NewReleasesWidget 
              title="🎬 Новинки"
              movies={data?.new_releases || []} 
              linkText="Календарь премьер"
              linkUrl="/new-releases"
            />
          </Col>
        </Row>

        {/* Статистика */}
        <Row className="mt-5">
          <Col>
            <div className="card bg-light">
              <div className="card-body text-center">
                <Row>
                  <Col md={3}>
                    <h4 className="text-primary">{data?.top_movies?.length || 0}</h4>
                    <small className="text-muted">Топ фильмов</small>
                  </Col>
                  <Col md={3}>
                    <h4 className="text-success">{data?.popular_genres?.length || 0}</h4>
                    <small className="text-muted">Популярных жанров</small>
                  </Col>
                  <Col md={3}>
                    <h4 className="text-warning">{data?.new_releases?.length || 0}</h4>
                    <small className="text-muted">Новинок</small>
                  </Col>
                  <Col md={3}>
                    <h4 className="text-info">
                      {(data?.top_movies?.length || 0) + (data?.new_releases?.length || 0)}
                    </h4>
                    <small className="text-muted">Всего фильмов</small>
                  </Col>
                </Row>
              </div>
            </div>
          </Col>
        </Row>
      </Container>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default HomePage; 