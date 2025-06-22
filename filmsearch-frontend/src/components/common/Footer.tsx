import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import './Footer.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const isAuthenticated = false; // Пока что статично
  const user = { username: 'Гость', isStaff: false, isSuperuser: false };

  return (
    <footer className="bg-dark text-light mt-5 py-4">
      <Container>
        <Row>
          <Col md={6}>
            <h5>
              <i className="fas fa-film me-2"></i>
              FilmSearch
            </h5>
            <p className="mb-3">
              Ваш персональный помощник в мире кино и сериалов
            </p>
            
            {/* Дополнительная информация */}
            <div className="footer-links">
              <small className="text-muted">
                <a href="#" className="text-muted me-3 text-decoration-none">
                  <i className="fas fa-info-circle me-1"></i>
                  О проекте
                </a>
                <a href="#" className="text-muted me-3 text-decoration-none">
                  <i className="fas fa-envelope me-1"></i>
                  Контакты
                </a>
                <a href="#" className="text-muted text-decoration-none">
                  <i className="fas fa-shield-alt me-1"></i>
                  Политика конфиденциальности
                </a>
              </small>
            </div>
          </Col>
          
          <Col md={6} className="text-end">
            <p className="mb-2">
              &copy; {currentYear} FilmSearch. Все права защищены.
            </p>
            
            {isAuthenticated ? (
              <small>
                Добро пожаловать, {user.username}!
                {(user.isStaff || user.isSuperuser) && (
                  <span className="admin-badge ms-2">АДМИНИСТРАТОР</span>
                )}
              </small>
            ) : (
              <small className="text-muted">
                <i className="fas fa-users me-1"></i>
                Присоединяйтесь к нашему сообществу любителей кино
              </small>
            )}
            
            {/* Социальные сети */}
            <div className="social-links mt-3">
              <a href="#" className="text-light me-3" title="VKontakte">
                <i className="fab fa-vk fa-lg"></i>
              </a>
              <a href="#" className="text-light me-3" title="Telegram">
                <i className="fab fa-telegram fa-lg"></i>
              </a>
              <a href="#" className="text-light me-3" title="YouTube">
                <i className="fab fa-youtube fa-lg"></i>
              </a>
              <a href="#" className="text-light" title="GitHub">
                <i className="fab fa-github fa-lg"></i>
              </a>
            </div>
          </Col>
        </Row>
        
        {/* Дополнительная строка со статистикой */}
        <Row className="mt-4 pt-3 border-top border-secondary">
          <Col className="text-center">
            <small className="text-muted">
              <span className="me-4">
                <i className="fas fa-film me-1"></i>
                1000+ фильмов
              </span>
              <span className="me-4">
                <i className="fas fa-tv me-1"></i>
                500+ сериалов
              </span>
              <span className="me-4">
                <i className="fas fa-users me-1"></i>
                10K+ пользователей
              </span>
              <span>
                <i className="fas fa-star me-1"></i>
                50K+ отзывов
              </span>
            </small>
          </Col>
        </Row>
             </Container>
    </footer>
  );
};

export default Footer; 