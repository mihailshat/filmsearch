import React, { useState } from 'react';
import { Navbar, Nav, NavDropdown, Container } from 'react-bootstrap';
import SearchBar from './SearchBar';
import './Header.css';

const Header: React.FC = () => {
  const [isAuthenticated] = useState(false); // Пока что статично
  const [user] = useState({ username: 'Гость', isStaff: false, isSuperuser: false });

  return (
    <>
      {/* Навигация */}
      <Navbar expand="lg" variant="dark" bg="dark" className="navbar-custom">
        <Container>
          <Navbar.Brand href="#" className="navbar-brand-custom">
            <i className="fas fa-film me-2"></i>
            FilmSearch
          </Navbar.Brand>
          
          <Navbar.Toggle aria-controls="navbarNav" />
          
          <Navbar.Collapse id="navbarNav">
            <Nav className="me-auto">
              <Nav.Link href="#" className="nav-link-custom">
                <i className="fas fa-home me-1"></i>
                Главная
              </Nav.Link>
              <Nav.Link href="#" className="nav-link-custom">
                <i className="fas fa-tags me-1"></i>
                Жанры
              </Nav.Link>
              <Nav.Link href="#" className="nav-link-custom">
                <i className="fas fa-users me-1"></i>
                Актеры
              </Nav.Link>
              <Nav.Link href="#" className="nav-link-custom">
                <i className="fas fa-list me-1"></i>
                Подборки
              </Nav.Link>
            </Nav>
            
            <Nav>
              {isAuthenticated ? (
                /* Меню для авторизованных пользователей */
                <NavDropdown 
                  title={
                    <>
                      <i className="fas fa-user me-1"></i>
                      {user.username}
                      {user.isStaff || user.isSuperuser ? (
                        <span className="admin-badge ms-2">АДМИН</span>
                      ) : (
                        <span className="user-badge ms-2">USER</span>
                      )}
                    </>
                  }
                  id="userDropdown"
                  align="end"
                >
                  <NavDropdown.Item href="#">
                    <i className="fas fa-user-circle me-2"></i>
                    Мой профиль
                  </NavDropdown.Item>
                  <NavDropdown.Item href="#">
                    <i className="fas fa-star me-2"></i>
                    Рекомендации
                  </NavDropdown.Item>
                  <NavDropdown.Divider />
                  
                  <NavDropdown.Header>Пользователь</NavDropdown.Header>
                  <NavDropdown.Item href="#">
                    <i className="fas fa-plus me-2"></i>
                    Создать подборку
                  </NavDropdown.Item>
                  
                  {(user.isStaff || user.isSuperuser) && (
                    <>
                      <NavDropdown.Divider />
                      <NavDropdown.Header>Администратор</NavDropdown.Header>
                      <NavDropdown.Item href="#">
                        <i className="fas fa-tachometer-alt me-2"></i>
                        Панель админа
                      </NavDropdown.Item>
                      <NavDropdown.Item href="#">
                        <i className="fas fa-plus-circle me-2"></i>
                        Добавить фильм
                      </NavDropdown.Item>
                      <NavDropdown.Item href="#">
                        <i className="fas fa-tag me-2"></i>
                        Добавить жанр
                      </NavDropdown.Item>
                      <NavDropdown.Item href="#">
                        <i className="fas fa-magic me-2"></i>
                        Генерировать рекомендации
                      </NavDropdown.Item>
                      {user.isSuperuser && (
                        <NavDropdown.Item href="#">
                          <i className="fas fa-users-cog me-2"></i>
                          Управление пользователями
                        </NavDropdown.Item>
                      )}
                    </>
                  )}
                  
                  <NavDropdown.Divider />
                  <NavDropdown.Item href="#">
                    <i className="fas fa-sign-out-alt me-2"></i>
                    Выйти
                  </NavDropdown.Item>
                </NavDropdown>
              ) : (
                /* Меню для неавторизованных пользователей */
                <>
                  <Nav.Link href="#" className="nav-link-custom">
                    <i className="fas fa-sign-in-alt me-1"></i>
                    Войти
                  </Nav.Link>
                  <Nav.Link href="#" className="nav-link-custom">
                    <i className="fas fa-user-plus me-1"></i>
                    Регистрация
                  </Nav.Link>
                </>
              )}
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Hero секция с поиском */}
      <div className="hero-section bg-primary text-white py-5">
        <Container>
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h1 className="display-4 fw-bold mb-3">
                <i className="fas fa-film me-3"></i>
                FilmSearch
              </h1>
              <p className="lead mb-4">
                Ваш персональный помощник в мире кино и сериалов
              </p>
              <div className="hero-stats">
                <div className="row text-center">
                  <div className="col-4">
                    <h4 className="text-warning">1000+</h4>
                    <small>Фильмов</small>
                  </div>
                  <div className="col-4">
                    <h4 className="text-warning">500+</h4>
                    <small>Сериалов</small>
                  </div>
                  <div className="col-4">
                    <h4 className="text-warning">50+</h4>
                    <small>Жанров</small>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="search-container bg-white p-4 rounded shadow">
                <h5 className="text-dark mb-3">
                  <i className="fas fa-search me-2"></i>
                  Найти фильм или сериал
                </h5>
                <SearchBar />
                <div className="mt-3">
                  <small className="text-muted">
                    Популярные запросы: 
                    <span className="badge bg-light text-dark ms-1 me-1">драма</span>
                    <span className="badge bg-light text-dark me-1">комедия</span>
                    <span className="badge bg-light text-dark me-1">2024</span>
                  </small>
                </div>
              </div>
            </div>
          </div>
        </Container>
             </div>
    </>
  );
};

export default Header; 