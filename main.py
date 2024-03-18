from selenium import webdriver  # ウェブブラウザ🌐を自動操作するためのツールをインポート
from selenium.webdriver.firefox.options import (
    Options,
)  # Firefoxブラウザ🌐のオプションを設定するためのツールをインポート
from selenium.webdriver.common.by import (
    By,
)  # HTML要素🔍を指定するための方法を提供するツールをインポート
from selenium.webdriver.support.ui import (
    WebDriverWait,
)  # 特定の条件が満たされるまで待つためのツールをインポート
from selenium.webdriver.support import (
    expected_conditions as EC,
)  # 特定の条件を指定するためのツールをインポート
from selenium.common.exceptions import (
    NoAlertPresentException,
    TimeoutException,
)  # 特定の例外を扱うためのツールをインポート
import time  # 時間⏰に関する操作を行うためのモジュールをインポート
import logging  # ログ📝を取るためのモジュールをインポート
import configparser  # 設定ファイル📁を扱うためのモジュールをインポート

# 設定ファイルを読み込む
config = configparser.ConfigParser()
config.read("config.ini")

# ログの設定を行う。ログレベル、フォーマットを指定
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.debug("設定ファイルを読み込みました。")


# TwitterBotクラスを定義
class TwitterBot:
    # 初期化メソッド。オブジェクトが生成された時に自動的に呼び出される
    def __init__(self, account):
        logging.debug("TwitterBotの初期化を開始します。")
        self.account = account  # アカウント情報👥
        self.driver = self._init_driver()  # WebDriverの初期化
        logging.debug("TwitterBotの初期化が完了しました。")

    # WebDriverを初期化するための内部メソッド
    def _init_driver(self):
        logging.debug("WebDriverの初期化を開始します。")
        firefox_options = Options()  # Firefoxのオプションを設定
        firefox_options.binary_location = config["BROWSER"][
            "tor_path"
        ]  # Torブラウザ🌐のパスを設定
        firefox_options.set_preference(
            "network.proxy.type", config.getint("PROXY", "type")
        )  # プロキシ設定を有効にする
        firefox_options.set_preference(
            "network.proxy.socks", config["PROXY"]["host"]
        )  # SOCKSプロキシのホストを設定
        firefox_options.set_preference(
            "network.proxy.socks_port", config.getint("PROXY", "port")
        )  # SOCKSプロキシのポートを設定
        firefox_options.set_preference(
            "intl.accept_languages", config["LANGUAGE"]["accept_languages"]
        )  # 言語設定を英語にする
        logging.debug("WebDriverのオプション設定が完了しました。")
        driver = webdriver.Firefox(options=firefox_options)  # Firefox WebDriverを返す
        logging.debug("WebDriverの初期化が完了しました。")
        return driver

    # ログイン処理を行うメソッド
    def login(self):
        logging.debug("ログイン処理を開始します。")
        self.driver.get(
            "https://twitter.com/login"
        )  # Twitterのログインページにアクセス
        logging.debug("Twitterのログインページにアクセスしました。")
        self._handle_alert()  # アラート処理を行う
        self._fill_login_form()  # ログインフォームを埋める
        self._submit_login_form()  # ログインフォームを送信する
        logging.debug("ログイン処理が完了しました。")

    # アラート処理を行う内部メソッド
    def _handle_alert(self):
        logging.debug("アラート処理を開始します。")
        try:
            alert = self.driver.switch_to.alert  # アラートがあれば取得
            alert.accept()  # アラートを承認
            logging.debug("アラートを承認しました。")
        except NoAlertPresentException:
            logging.info(
                "ログイン時にアラートは表示されませんでした。"
            )  # アラートがなければログに記録
        except Exception as e:
            logging.error(
                f"ログイン処理中に予期しないエラーが発生しました: {e}"
            )  # その他のエラーが発生した場合はログに記録

    # ログインフォームを埋める内部メソッド
    def _fill_login_form(self):
        logging.debug("ログインフォームの入力を開始します。")
        username_field = self.wait_for_element(
            (By.NAME, "session[username_or_email]"), condition="visible"
        )  # ユーザー名入力欄を待機して取得
        password_field = self.driver.find_element(
            By.NAME, "session[password]"
        )  # パスワード入力欄を取得
        username_field.send_keys(self.account["username"])  # ユーザー名を入力
        password_field.send_keys(self.account["password"])  # パスワードを入力
        logging.debug("ログインフォームの入力が完了しました。")

    # ログインフォームを送信する内部メソッド
    def _submit_login_form(self):
        logging.debug("ログインフォームの送信を開始します。")
        login_button = self.driver.find_element(
            By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]'
        )  # ログインボタンを取得
        login_button.click()  # ログインボタンをクリック
        logging.debug("ログインフォームを送信しました。")

    # いいねとリツイートを行うメソッド
    def like_and_retweet(self):
        logging.debug("いいねとリツイート処理を開始します。")
        try:
            like_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="like"]'), condition="clickable"
            )  # いいねボタンを待機して取得
            like_button.click()  # いいねボタンをクリック
            logging.debug("いいねをクリックしました。")
            retweet_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="retweet"]'), condition="clickable"
            )  # リツイートボタンを待機して取得
            retweet_button.click()  # リツイートボタンをクリック
            logging.debug("リツイートをクリックしました。")
            confirm_retweet_button = self.wait_for_element(
                (By.XPATH, '//div[@data-testid="retweetConfirm"]'),
                condition="clickable",
            )  # リツイート確認ボタンを待機して取得
            confirm_retweet_button.click()  # リツイート確認ボタンをクリック
            logging.debug("リツイート確認をクリックしました。")
        except Exception as e:
            logging.error(
                f"いいねやリツイート処理中にエラーが発生しました: {e}"
            )  # エラーが発生した場合はログに記録

    # 特定の要素が表示されるまで待つメソッド
    def wait_for_element(self, locator, timeout=15, condition="presence"):
        logging.debug(
            f"要素の待機を開始します。条件: {condition}, タイムアウト: {timeout}秒"
        )
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
        logging.debug("要素の待機が完了しました。")
        return element

    # ブラウザを閉じるメソッド
    def close(self):
        logging.debug("ブラウザを閉じる処理を開始します。")
        time.sleep(5)  # 5秒待機
        self.driver.quit()  # ブラウザを閉じる
        logging.debug("ブラウザを閉じました。")


# アカウント情報👥
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
    logging.debug(f"{account['username']}での処理を開始します。")
    bot = TwitterBot(account)  # TwitterBotオブジェクトを生成
    bot.login()  # ログインメソッドを呼び出し
    bot.like_and_retweet()  # いいねとリツイートメソッドを呼び出し
    bot.close()  # ブラウザを閉じるメソッドを呼び出し
    logging.debug(f"{account['username']}での処理が完了しました。")
