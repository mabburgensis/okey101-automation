# locators/okey101_locators.py

class RegisterLocators:
    # Header "Kayıt Ol" butonu
    REGISTER_BUTTON = '//*[@id="root"]/main/header/div/nav[2]/button[2]'
    # Kayıt modalı container
    REGISTER_MODAL_FORM = '//*[@id="root"]/div[2]/div/section'
    # Form alanları
    EMAIL_INPUT = '//*[@id="root"]/div[2]/div/section/div/form/div/label[1]/input'
    USERNAME_INPUT = '//*[@id="root"]/div[2]/div/section/div/form/div/label[2]/input'
    PASSWORD_INPUT = '//*[@id="root"]/div[2]/div/section/div/form/div/label[3]/input'
    # Submit
    SUBMIT_BUTTON = '//*[@id="root"]/div[2]/div/section/div/form/div/button'


class LoginLocators:
    # Header "Giriş Yap"
    LOGIN_BUTTON_HEADER = '//*[@id="root"]/main/header/div/nav[2]/button[1]'
    # Login modalı container
    LOGIN_MODAL_FORM = '//*[@id="root"]/div[2]/div/section'
    # Form alanları
    USERNAME_INPUT = '//*[@id="root"]/div[2]/div/section/div/form/div/label[1]/input'
    PASSWORD_INPUT = '//*[@id="root"]/div[2]/div/section/div/form/div/label[2]/input'
    # Submit
    LOGIN_SUBMIT_BUTTON = '//*[@id="root"]/div[2]/div/section/div/form/button'


class Okey101Locators:
    # Ana sayfadaki 101 banner (lobiye götürüyor)
    BANNER_101 = '//*[@id="root"]/main/div/div[2]/div/div[2]/a[1]/img'

    # TR "Masa Oluştur" veya EN "Create Table" yazan buton
    CREATE_TABLE_BUTTON = (
        "//button[.//div[normalize-space()='Masa Oluştur' "
        "or normalize-space()='Create Table']]"
    )

    # Masa oluştur modalı
    TABLE_NAME_INPUT = '//*[@id="root"]/div/div[2]/div/div/form/label/input'
    BET_AMOUNT_INPUT = '//*[@id="root"]/div/div[2]/div/div/form/div[1]/label[1]/input'

    # Dropdown'lar (şimdilik dokunmuyoruz, default’lar kalıyor)
    CURRENCY_DROPDOWN   = '//*[@id="headlessui-listbox-button-_r_k_"]'
    HAND_WAIT_DROPDOWN  = '//*[@id="headlessui-listbox-button-_r_q_"]'
    TIME_BANK_DROPDOWN  = '//*[@id="headlessui-listbox-button-_r_10_"]'

    # Oyuncu sayısı butonları
    PLAYER_COUNT_2 = '//*[@id="root"]/div/div[2]/div/div/form/div[3]/div[2]/button[1]/div[1]'
    PLAYER_COUNT_4 = '//*[@id="root"]/div/div[2]/div/div/form/div[3]/div[2]/button[2]/div[1]/div'

    # Modal içindeki "Masa Oluştur" submit
    CREATE_TABLE_SUBMIT_BUTTON = '//*[@id="root"]/div/div[2]/div/div/form/nav/button[2]/div'

    # Oda içi nickname ekranı
    TABLE_NICKNAME_INPUT = '//*[@id="root"]/div/div[2]/div/form/input'
    TABLE_NICKNAME_SUBMIT = '//*[@id="root"]/div/div[2]/div/form/button'
