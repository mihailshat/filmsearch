import React from 'react';
import { Card, ListGroup, Badge, Button } from 'react-bootstrap';
import { TopMoviesWidgetProps } from '../../types/api';

const TopMoviesWidget: React.FC<TopMoviesWidgetProps> = ({ 
  title, 
  movies, 
  linkText, 
  linkUrl 
}) => {
  const renderStars = (rating: number): string => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    let stars = '⭐'.repeat(fullStars);
    if (hasHalfStar) stars += '⭐';
    
    return stars;
  };

  const getMovieImage = (movie: any): string => {
    if (movie.poster_image) {
      return `http://localhost:8000${movie.poster_image}`;
    }
    if (movie.poster_url) {
      return movie.poster_url;
    }
    return 'https://via.placeholder.com/60x90/6c757d/ffffff?text=No+Image';
  };

  return (
    <Card className="h-100 shadow-sm">
      <Card.Header className="bg-primary text-white">
        <h5 className="mb-0">{title}</h5>
      </Card.Header>
      
      <Card.Body className="p-0">
        <ListGroup variant="flush">
          {movies.slice(0, 8).map((movie, index) => (
            <ListGroup.Item key={movie.id} className="d-flex align-items-center p-3">
              <div className="me-3">
                <span className="badge bg-primary rounded-pill">{index + 1}</span>
              </div>
              
              <div className="me-3">
                <img 
                  src={getMovieImage(movie)}
                  alt={movie.title}
                  style={{ width: '50px', height: '75px', objectFit: 'cover' }}
                  className="rounded"
                />
              </div>
              
              <div className="flex-grow-1">
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 className="mb-1 text-primary" style={{ cursor: 'pointer' }}>
                      {movie.title}
                    </h6>
                    {movie.title_english && (
                      <small className="text-muted d-block">
                        {movie.title_english}
                      </small>
                    )}
                    <small className="text-muted">
                      {new Date(movie.release_date).getFullYear()} • {movie.country}
                    </small>
                  </div>
                  
                  <div className="text-end">
                    {movie.avg_rating && (
                      <div>
                        <div className="text-warning">
                          {renderStars(movie.avg_rating)}
                        </div>
                        <small className="text-muted">
                          {movie.avg_rating.toFixed(1)} ({movie.ratings_count})
                        </small>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mt-2">
                  {movie.genres?.slice(0, 3).map((genre) => (
                    <Badge key={genre.id} bg="secondary" className="me-1">
                      {genre.name}
                    </Badge>
                  ))}
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="ms-2"
                    style={{ fontSize: '0.75rem' }}
                  >
                    ♡ В избранное
                  </Button>
                </div>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card.Body>
      
      {linkText && linkUrl && (
        <Card.Footer className="text-center">
          <Button variant="primary" href={linkUrl}>
            {linkText} →
          </Button>
        </Card.Footer>
      )}
    </Card>
  );
};

export default TopMoviesWidget; 