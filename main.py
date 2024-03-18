import configparser
import logging
import time
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 設定ファイルを読み込む
config = configparser.ConfigParser()
config.read("config.ini")

# ログの設定を行う
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.debug("設定ファイルを読み込みました")


class TwitterBot:
    def __init__(self, account):
        logging.debug(f"{account['username']} - TwitterBotの初期化を開始します")
        self.account = account
        self.driver = self._init_driver()
        logging.debug(f"{account['username']} - TwitterBotの初期化が完了しました")

    def _init_driver(self):
        logging.debug(f"{self.account['username']} - WebDriverの初期化を開始します")
        options = Options()
        options.binary_location = config["BROWSER"]["tor_path"]
        options.set_preference("network.proxy.type", config.getint("PROXY", "type"))
        options.set_preference("network.proxy.socks", config["PROXY"]["host"])
        options.set_preference(
            "network.proxy.socks_port", config.getint("PROXY", "port")
        )
        options.set_preference(
            "intl.accept_languages", config["LANGUAGE"]["accept_languages"]
        )

        profile_path = config["BROWSER"]["profile_path"]
        firefox_profile = FirefoxProfile(profile_path)
        options.profile = firefox_profile

        logging.debug(
            f"{self.account['username']} - WebDriverのオプション設定が完了しました"
        )
        driver = webdriver.Firefox(options=options)
        logging.debug(f"{self.account['username']} - WebDriverの初期化が完了しました")
        return driver

    def login(self):
        logging.debug(f"{self.account['username']} - ログイン処理を開始します")
        self.driver.get("https://twitter.com/login")
        logging.debug(
            f"{self.account['username']} - Twitterのログインページにアクセスしました"
        )
        self._handle_alert()
        self._fill_login_form()
        self._submit_login_form()
        logging.debug(f"{self.account['username']} - ログイン処理が完了しました")

    def _handle_alert(self):
        logging.debug(f"{self.account['username']} - アラート処理を開始します")
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            logging.debug(f"{self.account['username']} - アラートを承認しました")
        except NoAlertPresentException:
            logging.info(
                f"{self.account['username']} - ログイン時にアラートは表示されませんでした"
            )
        except Exception as e:
            logging.error(
                f"{self.account['username']} - ログイン処理中に予期しないエラーが発生しました: {type(e).__name__} - {str(e)}"
            )

    def _fill_login_form(self):
        logging.debug(
            f"{self.account['username']} - ログインフォームの入力を開始します"
        )
        try:
            username_field = self.wait_for_element(
                (By.NAME, "session[username_or_email]"), condition="visible"
            )
            password_field = self.driver.find_element(By.NAME, "session[password]")
            username_field.send_keys(self.account["username"])
            password_field.send_keys(self.account["password"])
            logging.debug(
                f"{self.account['username']} - ログインフォームの入力が完了しました"
            )
        except Exception as e:
            logging.error(
                f"{self.account['username']} - ログインフォームの入力中にエラーが発生しました: {type(e).__name__} - {str(e)}"
            )
            raise

    def _submit_login_form(self):
        logging.debug(
            f"{self.account['username']} - ログインフォームの送信を開始します"
        )
        try:
            login_button = self.driver.find_element(
                By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]'
            )
            login_button.click()
            logging.debug(
                f"{self.account['username']} - ログインフォームを送信しました"
            )
        except Exception as e:
            logging.error(
                f"{self.account['username']} - ログインフォームの送信中にエラーが発生しました: {type(e).__name__} - {str(e)}"
            )
            raise

    def like_and_retweet(self):
        logging.debug(
            f"{self.account['username']} - いいねとリツイート処理を開始します"
        )
        try:
            like_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="like"]'), condition="clickable"
            )
            like_button.click()
            logging.debug(f"{self.account['username']} - いいねをクリックしました")
        except Exception as e:
            logging.warning(
                f"{self.account['username']} - いいねボタンのクリック中にエラーが発生しました: {type(e).__name__} - {str(e)}"
            )

        try:
            retweet_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="retweet"]'), condition="clickable"
            )
            retweet_button.click()
            logging.debug(f"{self.account['username']} - リツイートをクリックしました")
        except Exception as e:
            logging.warning(
                f"{self.account['username']} - リツイートボタンのクリック中にエラーが発生しました: {type(e).__name__} - {str(e)}"
            )

        try:
            confirm_retweet_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="retweetConfirm"]'),
                condition="clickable",
            )
            confirm_retweet_button.click()
            logging.debug(
                f"{self.account['username']} - リツイート確認をクリックしました"
            )
        except Exception as e:
            logging.warning(
                f"{self.account['username']} - リツイート確認ボタンのクリック中にエラーが発生しました: {type(e).__name__} - {str(e)}"
            )

    def wait_for_element(self, locator, timeout=15, condition="presence"):
        logging.debug(
            f"{self.account['username']} - 要素の待機を開始します。条件: {condition}, タイムアウト: {timeout}秒"
        )
        try:
            if condition == "visible":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located(locator)
                )
            elif condition == "clickable":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
            logging.debug(f"{self.account['username']} - 要素の待機が完了しました")
            return element
        except TimeoutException:
            logging.warning(
                f"{self.account['username']} - 要素の待機がタイムアウトしました。条件: {condition}, タイムアウト: {timeout}秒"
            )
            return None

    def close(self):
        logging.debug(f"{self.account['username']} - ブラウザを閉じる処理を開始します")
        self.driver.quit()
        logging.debug(f"{self.account['username']} - ブラウザを閉じました")


# アカウント情報
accounts = [
    {
        "username": config["ACCOUNTS"]["account1_username"],
        "password": config["ACCOUNTS"]["account1_password"],
    },
    {
        "username": config["ACCOUNTS"]["account2_username"],
        "password": config["ACCOUNTS"]["account2_password"],
    },
]

# 各アカウントでログインし、いいねとリツイートを行う
for account in accounts:
    bot = TwitterBot(account)
    bot.login()
    bot.like_and_retweet()
    bot.close()
    time.sleep(5)  # アカウントの切り替え間隔
