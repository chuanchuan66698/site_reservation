import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeatReservation:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无头模式，取消注释即可启用
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def login(self):
        """登录系统"""
        try:
            self.driver.get(BASE_URL)
            logger.info("正在打开登录页面...")
            
            # 等待登录表单加载
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            # 输入登录信息
            username_input.send_keys(USERNAME)
            password_input.send_keys(PASSWORD)
            
            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
            login_button.click()
            
            logger.info("登录成功！")
            return True
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return False

    def navigate_to_reservation(self):
        """导航到预约页面"""
        try:
            self.driver.get(RESERVATION_URL)
            logger.info("正在进入预约页面...")
            time.sleep(2)  # 等待页面加载
            return True
        except Exception as e:
            logger.error(f"进入预约页面失败: {str(e)}")
            return False

    def select_seat(self):
        """选择座位"""
        try:
            # 等待座位列表加载
            seats = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "seat-item"))
            )
            
            # 优先选择偏好座位
            for seat in seats:
                seat_number = seat.get_attribute("data-seat-id")
                if seat_number in PREFERRED_SEATS and "available" in seat.get_attribute("class"):
                    seat.click()
                    logger.info(f"已选择座位: {seat_number}")
                    return True
            
            # 如果没有偏好座位，选择第一个可用座位
            for seat in seats:
                if "available" in seat.get_attribute("class"):
                    seat.click()
                    logger.info(f"已选择可用座位: {seat.get_attribute('data-seat-id')}")
                    return True
            
            logger.warning("没有找到可用座位")
            return False
        except Exception as e:
            logger.error(f"选择座位失败: {str(e)}")
            return False

    def confirm_reservation(self):
        """确认预约"""
        try:
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '确认预约')]"))
            )
            confirm_button.click()
            logger.info("预约确认成功！")
            return True
        except Exception as e:
            logger.error(f"确认预约失败: {str(e)}")
            return False

    def run(self):
        """运行预约流程"""
        try:
            if not self.login():
                return
            
            if not self.navigate_to_reservation():
                return
            
            # 等待预约时间
            while datetime.now().strftime("%H:%M:%S") < RESERVATION_START_TIME:
                time.sleep(0.1)
            
            if not self.select_seat():
                return
            
            if not self.confirm_reservation():
                return
            
            logger.info("预约流程完成！")
        except Exception as e:
            logger.error(f"预约过程出错: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    reservation = SeatReservation()
    reservation.run() 
