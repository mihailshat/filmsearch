import React from 'react';
import { Card, Row, Col, Badge, Button } from 'react-bootstrap';
import { NewReleasesWidgetProps } from '../../types/api';

const NewReleasesWidget: React.FC<NewReleasesWidgetProps> = ({ 
  title, 
  movies, 
  linkText, 
  linkUrl 
}) => {
  const getMovieImage = (movie: any): string => {
    if (movie.poster_image) {
      return `http://localhost:8000${movie.poster_image}`;
    }
    if (movie.poster_url) {
      return movie.poster_url;
    }
    return 'https://via.placeholder.com/150x225/6c757d/ffffff?text=No+Image';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const getDaysAgo = (dateString: string): number => {
    const releaseDate = new Date(dateString);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - releaseDate.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getTypeIcon = (type: string): string => {
    return type === 'movie' ? '🎬' : '📺';
  };

  const getTypeText = (type: string): string => {
    return type === 'movie' ? 'Фильм' : 'Сериал';
  };

  return (
    <Card className="h-100 shadow-sm">
      <Card.Header className="bg-warning text-dark">
        <h5 className="mb-0">{title}</h5>
      </Card.Header>
      
      <Card.Body>
        <Row>
          {movies.slice(0, 6).map((movie) => {
            const daysAgo = getDaysAgo(movie.release_date);
            
            return (
              <Col md={4} lg={2} key={movie.id} className="mb-4">
                <div className="text-center">
                  <div className="position-relative mb-2">
                    <img 
                      src={getMovieImage(movie)}
                      alt={movie.title}
                      style={{ 
                        width: '100%', 
                        height: '200px', 
                        objectFit: 'cover',
                        cursor: 'pointer'
                      }}
                      className="rounded shadow-sm"
                    />
                    
                    {/* Бейдж "Новинка" */}
                    {daysAgo <= 30 && (
                      <Badge 
                        bg="danger" 
                        className="position-absolute top-0 start-0 m-1"
                        style={{ fontSize: '0.7rem' }}
                      >
                        NEW
                      </Badge>
                    )}
                    
                    {/* Тип контента */}
                    <Badge 
                      bg="dark" 
                      className="position-absolute top-0 end-0 m-1"
                      style={{ fontSize: '0.7rem' }}
                    >
                      {getTypeIcon(movie.type)} {getTypeText(movie.type)}
                    </Badge>
                  </div>
                  
                  <div>
                    <h6 
                      className="text-primary mb-1" 
                      style={{ 
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        lineHeight: '1.2'
                      }}
                      title={movie.title}
                    >
                      {movie.title.length > 20 
                        ? `${movie.title.substring(0, 20)}...` 
                        : movie.title
                      }
                    </h6>
                    
                    {movie.title_english && (
                      <small className="text-muted d-block mb-1">
                        {movie.title_english.length > 25 
                          ? `${movie.title_english.substring(0, 25)}...` 
                          : movie.title_english
                        }
                      </small>
                    )}
                    
                    <small className="text-muted d-block mb-2">
                      {formatDate(movie.release_date)}
                    </small>
                    
                    <div className="mb-2">
                      {movie.genres?.slice(0, 2).map((genre) => (
                        <Badge key={genre.id} bg="secondary" className="me-1 mb-1" style={{ fontSize: '0.7rem' }}>
                          {genre.name}
                        </Badge>
                      ))}
                    </div>
                    
                    <Button 
                      variant="outline-warning" 
                      size="sm"
                      style={{ fontSize: '0.75rem' }}
                      className="w-100"
                    >
                      ♡ В избранное
                    </Button>
                  </div>
                </div>
              </Col>
            );
          })}
        </Row>
      </Card.Body>
      
      {linkText && linkUrl && (
        <Card.Footer className="text-center">
          <Button variant="warning" href={linkUrl}>
            {linkText} →
          </Button>
        </Card.Footer>
      )}
    </Card>
  );
};

export default NewReleasesWidget; 