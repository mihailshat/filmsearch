import React from 'react';
import { Card, ListGroup, Badge, Button, ProgressBar } from 'react-bootstrap';
import { PopularGenresWidgetProps } from '../../types/api';

const PopularGenresWidget: React.FC<PopularGenresWidgetProps> = ({ 
  title, 
  genres, 
  linkText, 
  linkUrl 
}) => {
  // Находим максимальное количество фильмов для расчета прогресс-бара
  const maxMoviesCount = Math.max(...genres.map(genre => genre.movies_count || 0));

  const getGenreIcon = (genreName: string): string => {
    const icons: { [key: string]: string } = {
      'драма': '🎭',
      'комедия': '😄',
      'боевик': '💥',
      'триллер': '😱',
      'фантастика': '🚀',
      'ужасы': '👻',
      'мелодрама': '💕',
      'детектив': '🔍',
      'фэнтези': '🧙‍♂️',
      'приключения': '🗺️',
      'военный': '⚔️',
      'история': '📜',
      'биография': '👤',
      'документальный': '📹',
      'мультфильм': '🎨',
      'семейный': '👨‍👩‍👧‍👦',
      'криминал': '🔫',
      'вестерн': '🤠',
      'спорт': '⚽',
      'музыка': '🎵'
    };
    
    return icons[genreName.toLowerCase()] || '🎬';
  };

  const getProgressVariant = (index: number): string => {
    const variants = ['primary', 'success', 'warning', 'info', 'secondary'];
    return variants[index % variants.length];
  };

  return (
    <Card className="h-100 shadow-sm">
      <Card.Header className="bg-success text-white">
        <h5 className="mb-0">{title}</h5>
      </Card.Header>
      
      <Card.Body className="p-0">
        <ListGroup variant="flush">
          {genres.slice(0, 10).map((genre, index) => {
            const progressPercent = maxMoviesCount > 0 
              ? ((genre.movies_count || 0) / maxMoviesCount) * 100 
              : 0;
              
            return (
              <ListGroup.Item key={genre.id} className="p-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <div className="d-flex align-items-center">
                    <span className="me-2" style={{ fontSize: '1.2rem' }}>
                      {getGenreIcon(genre.name)}
                    </span>
                    <h6 className="mb-0 text-primary" style={{ cursor: 'pointer' }}>
                      {genre.name}
                    </h6>
                  </div>
                  
                  <Badge bg={getProgressVariant(index)} className="ms-2">
                    {genre.movies_count || 0} фильмов
                  </Badge>
                </div>
                
                <ProgressBar 
                  now={progressPercent} 
                  variant={getProgressVariant(index)}
                  style={{ height: '6px' }}
                  className="mb-2"
                />
                
                <div className="d-flex justify-content-between align-items-center">
                  <small className="text-muted">
                    {progressPercent.toFixed(1)}% от топ-жанра
                  </small>
                  
                  <Button 
                    variant="outline-success" 
                    size="sm"
                    style={{ fontSize: '0.75rem' }}
                  >
                    Смотреть фильмы →
                  </Button>
                </div>
              </ListGroup.Item>
            );
          })}
        </ListGroup>
      </Card.Body>
      
      {linkText && linkUrl && (
        <Card.Footer className="text-center">
          <Button variant="success" href={linkUrl}>
            {linkText} →
          </Button>
        </Card.Footer>
      )}
    </Card>
  );
};

export default PopularGenresWidget; 