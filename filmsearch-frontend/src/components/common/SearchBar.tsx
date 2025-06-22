import React, { useState } from 'react';
import { Form, Button, InputGroup } from 'react-bootstrap';
import { homepageAPI } from '../../services/api';
import { SearchParams } from '../../types/api';

const SearchBar: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);

  const handleSearch = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      return;
    }

    try {
      setIsSearching(true);
      
      const searchParams: SearchParams = {
        q: searchQuery.trim()
      };
      
      const response = await homepageAPI.searchMovies(searchParams);
      
      // Здесь можно добавить логику для отображения результатов поиска
      // Например, перенаправление на страницу результатов или показ модального окна
      console.log('Search results:', response.data);
      
      // Временно показываем alert с результатами
      alert(`Найдено ${response.data.movies?.length || 0} фильмов по запросу "${searchQuery}"`);
      
    } catch (error) {
      console.error('Search error:', error);
      alert('Ошибка поиска. Попробуйте еще раз.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchQuery(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter') {
      handleSearch(e as any);
    }
  };

  return (
    <Form onSubmit={handleSearch}>
      <InputGroup>
        <Form.Control
          type="text"
          placeholder="Поиск фильмов и сериалов..."
          value={searchQuery}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          disabled={isSearching}
          style={{ 
            borderTopRightRadius: 0, 
            borderBottomRightRadius: 0 
          }}
        />
        <Button 
          variant="light" 
          type="submit"
          disabled={isSearching || !searchQuery.trim()}
          style={{ 
            borderTopLeftRadius: 0, 
            borderBottomLeftRadius: 0,
            borderLeft: 'none'
          }}
        >
          {isSearching ? (
            <>
              <span className="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Поиск...
            </>
          ) : (
            <>
              🔍 Найти
            </>
          )}
        </Button>
      </InputGroup>
    </Form>
  );
};

export default SearchBar; 