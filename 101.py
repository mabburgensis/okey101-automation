import os
import sys
import time
import random
import argparse
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from common.browser_utils import open_browser
from locators.okey101_locators import RegisterLocators, LoginLocators, Okey101Locators

# CI flag: CI ortamında human_delay devre dışı
CI_MODE = os.getenv("CI", "0") == "1"


def human_delay(min_s: float = 0.4, max_s: float = 1.2) -> None:
    if CI_MODE:
        return
    time.sleep(random.uniform(min_s, max_s))


def type_slow(element, text: str,
              min_char_delay: float = 0.04,
              max_char_delay: float = 0.12) -> None:
    if CI_MODE:
        element.send_keys(text)
        return
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(min_char_delay, max_char_delay))


@dataclass
class Player:
    role: str          # "HOST", "GUEST", "GUEST_1", ...
    driver: object
    wait: WebDriverWait
    email: str
    username: str
    password: str


# -------------------- UNIQUE DATA HELPERS --------------------


def _unique_suffix() -> str:
    now_ms = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"{now_ms}{rand}"[-8:]


def generate_valid_credentials():
    suffix = _unique_suffix()
    email = f"autotest{suffix}@example.com"
    username = f"autouser{suffix}"
    password = "Test123!"
    return email, username, password


def generate_table_name() -> str:
    suffix = _unique_suffix()
    return f"auto_table_{suffix}"


# -------------------- REGISTER FLOW --------------------


def open_register_modal(driver, wait: WebDriverWait) -> None:
    print("DEBUG | Opening registration modal...")
    human_delay()
    register_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, RegisterLocators.REGISTER_BUTTON))
    )
    register_btn.click()

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, RegisterLocators.EMAIL_INPUT)
        )
    )
    print("DEBUG | Registration modal is visible.")
    human_delay()


def get_register_form_elements(driver):
    email_el = driver.find_element(By.XPATH, RegisterLocators.EMAIL_INPUT)
    username_el = driver.find_element(By.XPATH, RegisterLocators.USERNAME_INPUT)
    password_el = driver.find_element(By.XPATH, RegisterLocators.PASSWORD_INPUT)
    submit_el = driver.find_element(By.XPATH, RegisterLocators.SUBMIT_BUTTON)
    return email_el, username_el, password_el, submit_el


def register_new_user(driver, wait: WebDriverWait):
    print("DEBUG | Starting positive registration flow...")
    open_register_modal(driver, wait)
    email_el, username_el, password_el, submit_el = get_register_form_elements(driver)

    email, username, password = generate_valid_credentials()
    print(f"DEBUG | Registering user: {email} | {username}")

    email_el.clear()
    human_delay()
    type_slow(email_el, email)

    human_delay()
    username_el.clear()
    human_delay()
    type_slow(username_el, username)

    human_delay()
    password_el.clear()
    human_delay()
    type_slow(password_el, password)

    human_delay()
    submit_el.click()
    print("DEBUG | Register submit clicked, waiting for modal to disappear...")

    try:
        WebDriverWait(driver, 40).until(
            EC.invisibility_of_element_located(
                (By.XPATH, RegisterLocators.REGISTER_MODAL_FORM)
            )
        )
        print("DEBUG | Registration modal closed, registration assumed successful.")
    except TimeoutException:
        print(
            "WARN  | Registration modal did not disappear within 40s. "
            "Continuing anyway (assuming registration succeeded)."
        )

    return email, username, password


# -------------------- LOGIN FLOW (optional) --------------------


def login_if_login_button_visible(driver, wait: WebDriverWait,
                                  username: str, password: str) -> None:
    print("DEBUG | Checking if login button is visible...")

    try:
        login_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, LoginLocators.LOGIN_BUTTON_HEADER)
            )
        )
    except TimeoutException:
        print("DEBUG | Login button not found; assuming already logged in. Skipping login.")
        return

    human_delay()
    login_btn.click()

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, LoginLocators.USERNAME_INPUT)
        )
    )
    print("DEBUG | Login modal is visible.")
    human_delay()

    username_el = driver.find_element(By.XPATH, LoginLocators.USERNAME_INPUT)
    password_el = driver.find_element(By.XPATH, LoginLocators.PASSWORD_INPUT)
    submit_el = driver.find_element(By.XPATH, LoginLocators.LOGIN_SUBMIT_BUTTON)

    username_el.clear()
    human_delay()
    type_slow(username_el, username)

    human_delay()
    password_el.clear()
    human_delay()
    type_slow(password_el, password)

    human_delay()
    submit_el.click()
    print("DEBUG | Login submit clicked, waiting for modal to disappear...")

    wait.until(
        EC.invisibility_of_element_located(
            (By.XPATH, LoginLocators.LOGIN_MODAL_FORM)
        )
    )
    print("DEBUG | Login completed (modal closed).")


# -------------------- 101 LOBBY & NICKNAME --------------------


def _handle_lobby_nickname(player: Player) -> None:
    """
    101 banner'a tıklandıktan sonra gelen 'Set your nickname' popup'ını
    bulup username'i yazar ve Save'e basar. Popup yoksa sessizce döner.
    """
    driver, wait = player.driver, player.wait
    print(f"DEBUG | {player.role}: Checking for lobby nickname popup...")

    input_locator = (By.XPATH, Okey101Locators.LOBBY_NICKNAME_INPUT)
    button_locator = (By.XPATH, Okey101Locators.LOBBY_NICKNAME_SAVE_BUTTON)

    driver.switch_to.default_content()

    # Önce default content
    try:
        nickname_el = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(input_locator)
        )
        print(f"DEBUG | {player.role}: Lobby nickname input found in default content.")
    except TimeoutException:
        nickname_el = None
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"DEBUG | {player.role}: Lobby nickname not in default content, checking {len(frames)} iframe(s)...")
        for idx, frame in enumerate(frames):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                frame_wait = WebDriverWait(driver, 3)
                nickname_el = frame_wait.until(
                    EC.presence_of_element_located(input_locator)
                )
                print(f"DEBUG | {player.role}: Lobby nickname input found in iframe index {idx}.")
                break
            except TimeoutException:
                continue

        if nickname_el is None:
            driver.switch_to.default_content()
            print(f"DEBUG | {player.role}: Lobby nickname popup not found; probably already set.")
            return

    # Doğru context'teyiz, şimdi Save butonunu alalım
    try:
        button_el = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(button_locator)
        )
    except TimeoutException:
        print(f"WARN  | {player.role}: Lobby nickname Save button not found.")
        return

    human_delay()
    nickname_el.clear()
    human_delay()
    type_slow(nickname_el, player.username)

    human_delay()
    button_el.click()
    print(f"DEBUG | {player.role}: Lobby nickname saved, waiting for popup to close...")

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located(input_locator)
    )
    print(f"DEBUG | {player.role}: Lobby nickname popup closed.")
    driver.switch_to.default_content()


def go_to_101_lobby(player: Player) -> None:
    """
    Her oyuncu için:
    1) 101 banner'a tıkla
    2) Nickname popup'ı varsa doldur + Save
    3) Son olarak 101 lobisinde CREATE_TABLE_BUTTON görünene kadar bekle
       (default content + iframe fallback)
    """
    driver, wait = player.driver, player.wait
    print(f"DEBUG | {player.role}: Navigating to 101 lobby...")
    human_delay()

    banner = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, Okey101Locators.BANNER_101)
        )
    )
    banner.click()
    print(f"DEBUG | {player.role}: 101 banner clicked, handling nickname & waiting for lobby...")

    # 1) Önce nickname popup'ını handle et
    _handle_lobby_nickname(player)

    # 2) Şimdi CREATE_TABLE_BUTTON görünene kadar bekle
    driver.switch_to.default_content()
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, Okey101Locators.CREATE_TABLE_BUTTON)
            )
        )
        print(f"DEBUG | {player.role}: 101 lobby visible in default content.")
        human_delay()
        return
    except TimeoutException:
        print(f"DEBUG | {player.role}: CREATE_TABLE_BUTTON not in default content. Trying iframes...")

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"DEBUG | {player.role}: Found {len(frames)} iframe(s).")

    for idx, frame in enumerate(frames):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame)
            frame_wait = WebDriverWait(driver, 10)
            frame_wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, Okey101Locators.CREATE_TABLE_BUTTON)
                )
            )
            print(f"DEBUG | {player.role}: 101 lobby found in iframe index {idx}.")
            human_delay()
            return
        except TimeoutException:
            continue

    driver.switch_to.default_content()
    raise TimeoutException(
        "CREATE_TABLE_BUTTON could not be found in default content or any iframe."
    )


def is_101_lobby_visible(player: Player, short_timeout: float = 2.0) -> bool:
    driver = player.driver
    locator = (By.XPATH, Okey101Locators.CREATE_TABLE_BUTTON)

    driver.switch_to.default_content()
    try:
        WebDriverWait(driver, short_timeout).until(
            EC.presence_of_element_located(locator)
        )
        return True
    except TimeoutException:
        pass

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for frame in frames:
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(frame)
            WebDriverWait(driver, short_timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            continue

    driver.switch_to.default_content()
    return False


def _table_row_xpath(table_name: str) -> str:
    return f"//table//tr[.//td[1][normalize-space()='{table_name}']]"


# -------------------- HOST TABLE CREATION --------------------


def host_create_table(host: Player, total_players: int) -> str:
    driver, wait = host.driver, host.wait
    print(f"DEBUG | {host.role}: Creating table for {total_players} players...")
    human_delay()

    create_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, Okey101Locators.CREATE_TABLE_BUTTON)
        )
    )
    create_btn.click()

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, Okey101Locators.TABLE_NAME_INPUT)
        )
    )
    print("DEBUG | Table creation modal is visible.")
    human_delay()

    table_name_el = driver.find_element(By.XPATH, Okey101Locators.TABLE_NAME_INPUT)
    bet_amount_el = driver.find_element(By.XPATH, Okey101Locators.BET_AMOUNT_INPUT)

    table_name = generate_table_name()
    table_name_el.clear()
    human_delay()
    type_slow(table_name_el, table_name)

    human_delay()
    bet_amount_el.clear()
    human_delay()
    type_slow(bet_amount_el, "10")

    human_delay()
    if total_players == 2:
        player_count_el = driver.find_element(By.XPATH, Okey101Locators.PLAYER_COUNT_2)
        print("DEBUG | Selecting 2-player table.")
    elif total_players == 4:
        player_count_el = driver.find_element(By.XPATH, Okey101Locators.PLAYER_COUNT_4)
        print("DEBUG | Selecting 4-player table.")
    else:
        raise ValueError(f"Unsupported total_players value: {total_players}")

    human_delay()
    player_count_el.click()

    human_delay()
    submit_el = driver.find_element(By.XPATH, Okey101Locators.CREATE_TABLE_SUBMIT_BUTTON)
    submit_el.click()
    print("DEBUG | Create Table submit clicked, waiting for modal to close...")

    wait.until(
        EC.invisibility_of_element_located(
            (By.XPATH, Okey101Locators.TABLE_NAME_INPUT)
        )
    )
    print("DEBUG | Table creation modal closed; host has entered the table view.")

    return table_name


# -------------------- GUEST JOIN TABLE --------------------


def guest_join_table(guest: Player, table_name: str) -> None:
    driver, wait = guest.driver, guest.wait
    print(f"DEBUG | {guest.role}: Joining table '{table_name}'...")
    human_delay()

    row_xpath = _table_row_xpath(table_name)

    wait.until(
        EC.presence_of_element_located((By.XPATH, row_xpath))
    )

    join_btn_xpath = f"{row_xpath}//td[last()]//button"
    join_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, join_btn_xpath))
    )

    human_delay()
    join_btn.click()
    print(f"DEBUG | {guest.role}: Clicked join button for table '{table_name}'.")


# -------------------- GAME END WAIT --------------------


def wait_for_game_end(host: Player,
                      poll_interval: int = 10,
                      max_wait_minutes: int = 40) -> None:
    print("INFO | Game is now running.")
    print("INFO | Waiting for host to return to 101 lobby to end the script...")

    start = time.time()
    while True:
        if is_101_lobby_visible(host, short_timeout=2.0):
            print("INFO | Host is back in 101 lobby. Game assumed finished.")
            break

        elapsed_min = (time.time() - start) / 60.0
        if elapsed_min > max_wait_minutes:
            print(
                f"WARN | Waited {max_wait_minutes} minutes, lobby not detected. "
                "Stopping script anyway."
            )
            break

        print(f"DEBUG | Game still running (lobby not visible). "
              f"Sleeping {poll_interval} seconds...")
        time.sleep(poll_interval)


# -------------------- PLAYER CREATION --------------------


def create_player(role: str) -> Player:
    driver, wait = open_browser()
    print(f"DEBUG | Creating player for role={role}")

    email, username, password = register_new_user(driver, wait)
    login_if_login_button_visible(driver, wait, username, password)

    print(f"DEBUG | {role} ready as {username}")
    return Player(
        role=role,
        driver=driver,
        wait=wait,
        email=email,
        username=username,
        password=password,
    )


# -------------------- ARG PARSING --------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="DracoFusion 101 Okey multi-user setup."
    )
    parser.add_argument(
        "--guests",
        type=int,
        help="Number of guest players (must be 1 or 3). Total players = 1 host + guests.",
    )
    args = parser.parse_args()

    if args.guests is None:
        print(
            "INFO | This script needs the --guests parameter (1 or 3). "
            "Example: python 101.py --guests 1"
        )
        sys.exit(1)

    if args.guests not in (1, 3):
        print(
            f"INFO | Invalid --guests value: {args.guests}. "
            "It must be 1 or 3 (1 host + guests = 2 or 4 players)."
        )
        sys.exit(1)

    return args


# -------------------- MAIN --------------------


def main():
    args = parse_args()
    guest_count = args.guests
    total_players = 1 + guest_count  # 2 or 4

    host = None
    guests = []

    try:
        # Host
        host = create_player("HOST")

        # Guests
        for i in range(guest_count):
            role = "GUEST" if guest_count == 1 else f"GUEST_{i + 1}"
            guests.append(create_player(role))

        print("\n=== Player Summary ===")
        print(f"HOST      : {host.username} ({host.email})")
        for g in guests:
            print(f"{g.role:9}: {g.username} ({g.email})")
        print(f"Total players planned for table: {total_players}")
        print("===============================\n")

        # Herkesi 101 lobisine taşı (banner + nickname + lobby)
        all_players = [host] + guests
        for p in all_players:
            go_to_101_lobby(p)

        # Host masa açar
        table_name = host_create_table(host, total_players)
        print(f"DEBUG | Host created table '{table_name}'.")
        
        time.sleep(3)

        # Tüm guest'ler masaya oturur
        for g in guests:
            guest_join_table(g, table_name)

        print("DEBUG | All guests attempted to join the host table.")

        # Oyun başladı; host'un tekrar lobide görünmesini bekle
        wait_for_game_end(host, poll_interval=10, max_wait_minutes=40)

    finally:
        if host and getattr(host, "driver", None):
            host.driver.quit()
            print("DEBUG | HOST driver quit.")
        for g in guests:
            if getattr(g, "driver", None):
                g.driver.quit()
                print(f"DEBUG | {g.role} driver quit.")


if __name__ == "__main__":
    main()
