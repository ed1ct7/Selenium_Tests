from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import random


def setup_firefox_driver():
    firefox_options = Options()

    # отключение сохранения паролей и уведомлений
    firefox_options.set_preference("signon.rememberSignons", False)
    firefox_options.set_preference("signon.autologin.proxy", False)
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)

    # отключение предупреждений безопасности
    firefox_options.set_preference("dom.disable_beforeunload", True)
    firefox_options.set_preference("browser.tabs.warnOnClose", False)

    driver = webdriver.Firefox(options=firefox_options)
    driver.maximize_window()  # максимизация окна для стабильности
    return driver


def test_login(driver):
    """1. Тест входа в систему"""
    try:
        print("=" * 50)
        print("Тест входа в систему")

        driver.get("https://www.saucedemo.com/")

        # ожидание и заполнение полей
        username = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-name"))
        )
        password = driver.find_element(By.ID, "password")

        username.send_keys("standard_user")
        password.send_keys("secret_sauce")

        # клик по кнопке входа
        login_btn = driver.find_element(By.ID, "login-button")
        login_btn.click()

        # проверка успешного входа
        WebDriverWait(driver, 10).until(
            EC.url_contains("inventory")
        )
        print("Тест входа пройден")
        return True

    except Exception as e:
        print(f"Ошибка входа: {e}")
        return False


def test_product_sorting(driver):
    """2. Тест сортировки товаров"""
    try:
        print("=" * 50)
        print("Тест сортировки товаров")

        # получение текущих цен до сортировки
        prices_before = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        prices_before_list = [price.text for price in prices_before]
        print(f"Цены до сортировки: {prices_before_list}")

        # использование Select для работы с выпадающим списком
        sort_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "product_sort_container"))
        )
        select = Select(sort_dropdown)

        # выбор сортировки по цене (от низкой к высокой)
        select.select_by_value("lohi")

        # ожидание применения сортировки с явным ожиданием изменения цен
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_elements(By.CLASS_NAME, "inventory_item_price")[0].text != prices_before_list[0]
        )

        # получение цен после сортировки
        prices_after = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
        prices_after_list = [price.text for price in prices_after]
        print(f"Цены после сортировки: {prices_after_list}")

        # преобразование цен в числа для проверки сортировки
        prices_after_numeric = [float(price.text.replace('$', '')) for price in prices_after]

        # проверка отсортированности цен по возрастанию
        is_sorted = all(prices_after_numeric[i] <= prices_after_numeric[i + 1]
                        for i in range(len(prices_after_numeric) - 1))

        if is_sorted:
            print("Сортировка товаров выполнена")
            return True
        else:
            print("Цены не отсортированы по возрастанию")
            return False

    except Exception as e:
        print(f"Ошибка сортировки товаров: {e}")
        return False


def test_view_product_details(driver):
    """3. Тест просмотра деталей товара"""
    try:
        print("=" * 50)
        print("Тест просмотра деталей товара")

        # выбор случайного товара для просмотра
        product_names = driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        if not product_names:
            print("Товары не найдены")
            return False

        random_product = random.choice(product_names)
        product_name = random_product.text
        print(f"Выбран товар: {product_name}")

        # клик по названию товара для просмотра деталей
        random_product.click()

        # проверка перехода на страницу деталей товара
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_details"))
        )

        # проверка совпадения названия товара
        detail_name = driver.find_element(By.CLASS_NAME, "inventory_details_name").text
        if product_name == detail_name:
            print("Детали товара загружены корректно")

            # возврат к списку товаров
            back_button = driver.find_element(By.ID, "back-to-products")
            back_button.click()

            # проверка возврата
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
            )
            print("Успешный возврат к списку товаров")
            return True
        else:
            print("Название товара не совпадает")
            return False

    except Exception as e:
        print(f"Ошибка просмотра деталей товара: {e}")
        return False


def test_add_multiple_to_cart(driver):
    """4. Тест добавления нескольких товаров в корзину"""
    try:
        print("=" * 50)
        print("Тест добавления нескольких товаров в корзину")

        # добавление нескольких товаров в корзину
        add_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to cart')]")

        if len(add_buttons) < 2:
            print("Недостаточно товаров для добавления")
            return False

        # добавление первых 3 товаров
        items_to_add = min(3, len(add_buttons))
        products_added = []

        for i in range(items_to_add):
            product_name = driver.find_elements(By.CLASS_NAME, "inventory_item_name")[i].text
            add_buttons[i].click()
            products_added.append(product_name)
            print(f"Добавлен товар: {product_name}")
            time.sleep(0.5)

        # проверка счетчика корзины
        cart_badge = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
        )

        cart_count = int(cart_badge.text)
        if cart_count == items_to_add:
            print(f"В корзине {cart_count} товаров")
            return True
        else:
            print(f"Неверное количество товаров в корзине: {cart_count}")
            return False

    except Exception as e:
        print(f"Ошибка добавления товаров в корзину: {e}")
        return False


def test_remove_from_cart(driver):
    """5. Тест удаления товаров из корзины"""
    try:
        print("=" * 50)
        print("Тест удаления товаров из корзины")

        # переход в корзину
        cart_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link"))
        )
        cart_icon.click()

        # проверка перехода в корзину
        WebDriverWait(driver, 10).until(
            EC.url_contains("cart")
        )

        # получение количества товаров в корзине
        cart_items = driver.find_elements(By.CLASS_NAME, "cart_item")
        initial_count = len(cart_items)
        print(f"Товаров в корзине: {initial_count}")

        if initial_count == 0:
            print("Корзина пуста")
            return False

        # удаление первого товара
        remove_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Remove')]")
        if remove_buttons:
            item_name = driver.find_elements(By.CLASS_NAME, "inventory_item_name")[0].text
            remove_buttons[0].click()
            print(f"Удален товар: {item_name}")

            # ожидание обновления корзины
            time.sleep(2)

            # проверка обновленного количества
            updated_cart_items = driver.find_elements(By.CLASS_NAME, "cart_item")
            updated_count = len(updated_cart_items)

            if updated_count == initial_count - 1:
                print("Товар успешно удален из корзины")

                # возврат к товарам
                continue_shopping = driver.find_element(By.ID, "continue-shopping")
                continue_shopping.click()

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
                )
                return True
            else:
                print("Количество товаров не изменилось")
                return False
        else:
            print("Нет товаров для удаления")
            return False

    except Exception as e:
        print(f"Ошибка удаления из корзины: {e}")
        return False


def test_checkout_process(driver):
    """6. Тест полного процесса оформления заказа"""
    try:
        print("=" * 50)
        print("Тест оформления заказов")

        # добавление товара для заказа (если корзина пуста)
        try:
            cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
            cart_count = int(cart_badge.text)
            if cart_count == 0:
                add_button = driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack")
                add_button.click()
                print("Добавлен товар для тестирования заказа")
        except:
            add_button = driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack")
            add_button.click()
            print("Добавлен товар для тестирования заказа")

        # переход в корзину
        cart_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link"))
        )
        cart_icon.click()

        # начало оформления
        checkout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "checkout"))
        )
        checkout_btn.click()

        # заполнение информации
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "first-name"))
        )

        driver.find_element(By.ID, "first-name").send_keys("Иван")
        driver.find_element(By.ID, "last-name").send_keys("Петров")
        driver.find_element(By.ID, "postal-code").send_keys("123456")

        time.sleep(1)

        # продолжение оформления
        continue_btn = driver.find_element(By.ID, "continue")
        continue_btn.click()

        # ожидание перехода на следующую страницу
        WebDriverWait(driver, 10).until(
            EC.url_contains("checkout-step-two")
        )

        # проверка итогов заказа
        summary_info = driver.find_element(By.CLASS_NAME, "summary_info").text
        print("Итоги заказа отображены")

        # завершение заказа
        finish_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "finish"))
        )
        finish_btn.click()

        # проверка успешного завершения
        WebDriverWait(driver, 10).until(
            EC.url_contains("checkout-complete")
        )

        success_msg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "complete-header"))
        )

        if "Thank you for your order" in success_msg.text:
            print("Заказ успешно оформлен")
            return True
        else:
            print("Сообщение об успехе не найдено")
            return False

    except Exception as e:
        print(f"Ошибка при оформлении заказа: {e}")
        return False


def test_user_profile(driver):
    """7. Тест работы с профилем пользователя"""
    try:
        print("=" * 50)
        print("Тест работы с профилем")

        # открытие бокового меню
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))
        )
        menu_button.click()

        # проверка элементов меню
        menu_items = driver.find_elements(By.CLASS_NAME, "menu-item")
        print("Доступные пункты меню:")
        for item in menu_items:
            print(f"  - {item.text}")

        # закрытие меню
        close_button = driver.find_element(By.ID, "react-burger-cross-btn")
        close_button.click()

        print("Работа с меню пользователя выполнена")
        return True

    except Exception as e:
        print(f"Ошибка работы с профилем: {e}")
        return False


def test_logout(driver):
    """8. Тест выхода из системы"""
    try:
        print("=" * 50)
        print("Тыст выхода из системы")

        # открытие меню
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "react-burger-menu-btn"))
        )
        menu_button.click()

        # выход из системы
        logout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
        )
        logout_btn.click()

        # проверка возврата на страницу логина
        WebDriverWait(driver, 10).until(
            EC.url_matches("https://www.saucedemo.com/")
        )

        # проверка наличия элементов страницы логина
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-button"))
        )

        username_field = driver.find_element(By.ID, "user-name")
        password_field = driver.find_element(By.ID, "password")

        if (login_button.is_displayed() and
                username_field.is_displayed() and
                password_field.is_displayed()):
            print("Выход из системы выполнен успешно")
            return True
        else:
            print("Не вернулись на страницу логина")
            return False

    except Exception as e:
        print(f"Ошибка выхода из системы: {e}")
        print(f"Текущий URL: {driver.current_url}")
        return False


def main():
    """Основная функция запуска тестов"""
    driver = None
    tests_passed = 0
    tests_failed = 0

    try:
        # использование Firefox вместо Chrome
        driver = setup_firefox_driver()

        # запуск тестов в логической последовательности
        tests = [
            ("Вход в систему", test_login),
            ("Сортировка товаров", test_product_sorting),
            ("Просмотр деталей товара", test_view_product_details),
            ("Добавление товаров в корзину", test_add_multiple_to_cart),
            ("Удаление из корзины", test_remove_from_cart),
            ("Оформление заказа", test_checkout_process),
            ("Работа с профилем", test_user_profile),
            ("Выход из системы", test_logout),
        ]

        for test_name, test_func in tests:
            if test_func(driver):
                tests_passed += 1
            else:
                tests_failed += 1
            time.sleep(2)  # пауза между тестами

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        tests_failed += 1
    finally:
        # итоги тестирования
        print("=" * 50)
        print("Итоги тестирования:")
        print(f"Успешно пройдено: {tests_passed}")
        print(f"Провалено: {tests_failed}")
        print(f"Общее количество тестов: {tests_passed + tests_failed}")
        print("=" * 50)

        if driver:
            driver.quit()
            print("Браузер закрыт")

if __name__ == "__main__":
    main()