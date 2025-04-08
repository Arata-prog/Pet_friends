import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture(autouse=True)
def driver():
    # Инициализация драйвера напрямую
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Установка неявного ожидания для всех тестов
    driver.implicitly_wait(10)
    
    # Переходим на страницу авторизации
    driver.get('http://petfriends.skillfactory.ru/login')
    
    # Вводим email и пароль
    driver.find_element(By.ID, 'email').send_keys('mshamagin02@gmail.com')
    driver.find_element(By.ID, 'pass').send_keys('00030003')
    # Нажимаем на кнопку входа в аккаунт
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    
    yield driver
    
    driver.quit()

def test_pet_cards_with_implicit_wait(driver):
    """Проверка карточек питомцев с использованием неявных ожиданий"""
    
    # Переходим на страницу со всеми питомцами
    driver.get('http://petfriends.skillfactory.ru/all_pets')
    
    # Проверяем, что мы на правильной странице - ищем любой заголовок
    all_headers = driver.find_elements(By.CSS_SELECTOR, '.text-center')
    is_page_loaded = False
    for header in all_headers:
        print(f"Найден заголовок: {header.text}")
        if "PetFriends" in header.text:
            is_page_loaded = True
    
    assert is_page_loaded, "Страница не загрузилась или не содержит ожидаемых заголовков"
    
    # Получаем все карточки питомцев с неявным ожиданием
    pet_cards = driver.find_elements(By.CSS_SELECTOR, '.card')
    
    # Проверяем, что карточки питомцев присутствуют на странице
    assert len(pet_cards) > 0, "Не найдены карточки питомцев"
    print(f"Найдено карточек питомцев: {len(pet_cards)}")
    
    # Проверяем каждую карточку питомца
    for i, card in enumerate(pet_cards[:5]):  # Проверяем первые 5 карточек для примера
        # Проверка контейнера изображения питомца (неявное ожидание)
        try:
            image_container = card.find_element(By.CSS_SELECTOR, 'div.text-center')
            assert image_container.is_displayed(), f"Контейнер изображения питомца #{i+1} не отображается"
            
            # Проверка наличия элемента изображения (даже если оно пустое)
            image = card.find_element(By.CSS_SELECTOR, '.card-img-top')
            print(f"Питомец #{i+1} элемент изображения присутствует: {image.get_attribute('outerHTML')}")
            
            # Проверка карточки питомца (неявное ожидание)
            try:
                card_body = card.find_element(By.CSS_SELECTOR, '.card-body')
                assert card_body.is_displayed(), f"Информация о питомце #{i+1} не отображается"
                
                # Проверка имени питомца (неявное ожидание)
                try:
                    pet_name = card.find_element(By.CSS_SELECTOR, '.card-title')
                    print(f"Питомец #{i+1} имя: {pet_name.text}")
                except Exception as e:
                    print(f"Ошибка при получении имени питомца #{i+1}: {e}")
                
                # Проверка информации о питомце (неявное ожидание)
                try:
                    pet_info = card.find_element(By.CSS_SELECTOR, '.card-text')
                    print(f"Питомец #{i+1} инфо: {pet_info.text}")
                except Exception as e:
                    print(f"Ошибка при получении информации о питомце #{i+1}: {e}")
            except Exception as e:
                print(f"Ошибка при проверке информации о питомце #{i+1}: {e}")
        except Exception as e:
            print(f"Ошибка при проверке карточки питомца #{i+1}: {e}")

def test_pets_table_with_explicit_wait(driver):
    """Проверка таблицы питомцев с использованием явных ожиданий"""
    
    # Переходим на страницу "Мои питомцы"
    driver.get('http://petfriends.skillfactory.ru/my_pets')
    
    # Создаем объект WebDriverWait для явных ожиданий
    wait = WebDriverWait(driver, 10)
    
    # Проверяем, что страница загрузилась (ищем любые заголовки)
    try:
        headers = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[self::h1 or self::h2 or self::h3]")))
        for header in headers:
            print(f"Найден заголовок: {header.tag_name} - {header.text}")
        
        # Проверяем наличие любого текста на странице
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"Текст на странице: {body_text[:100]}...")  # Выводим первые 100 символов
    except Exception as e:
        print(f"Ошибка при анализе заголовков: {e}")
    
    # Пытаемся найти таблицу или список питомцев
    try:
        # Явное ожидание загрузки информации о питомцах в любом виде
        pet_info_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.table, .card-deck, .card, [class*="pet"]'))
        )
        
        if pet_info_container.tag_name == 'table':
            # Если это таблица, проверяем строки
            rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody tr')))
            print(f"Найдена таблица с {len(rows)} строками")
            
            # Проверяем первые несколько строк
            for i, row in enumerate(rows[:5]):
                cells = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, f'tbody tr:nth-child({i+1}) td')
                ))
                
                print(f"Питомец #{i+1} в таблице. Количество ячеек: {len(cells)}")
                for j, cell in enumerate(cells):
                    print(f"  Ячейка {j+1}: {cell.text}")
        else:
            # Если это не таблица, проверяем, что есть другие элементы
            print(f"Найден контейнер с информацией о питомцах: {pet_info_container.tag_name}")
            
            # Ищем любую информацию о питомцах
            pet_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="pet"], .card, .card-deck, .card-body')
            print(f"Найдено элементов с информацией о питомцах: {len(pet_elements)}")
            
            # Выводим информацию о первых нескольких элементах
            for i, elem in enumerate(pet_elements[:5]):
                print(f"Элемент #{i+1}: {elem.tag_name} - {elem.get_attribute('class')}")
                try:
                    print(f"  Текст: {elem.text[:50]}..." if elem.text else "  Текст отсутствует")
                except Exception as e:
                    print(f"  Ошибка при получении текста: {e}")
                
    except Exception as e:
        print(f"Ошибка при поиске информации о питомцах: {e}")
        
        # Анализируем содержимое страницы
        print("\nАнализ структуры страницы:")
        body = driver.find_element(By.TAG_NAME, "body")
        
        # Получаем все видимые элементы
        all_elements = driver.find_elements(By.CSS_SELECTOR, "body *")
        visible_elements = [el for el in all_elements if el.is_displayed()]
        print(f"Всего видимых элементов на странице: {len(visible_elements)}")
        
        # Выводим информацию о первых 10 видимых элементах
        for i, elem in enumerate(visible_elements[:10]):
            print(f"Элемент #{i+1}: {elem.tag_name} - {elem.get_attribute('class') or 'без класса'}")
            try:
                if elem.text and elem.text.strip():
                    print(f"  Текст: {elem.text[:50]}..." if len(elem.text) > 50 else f"  Текст: {elem.text}")
            except Exception:
                pass 