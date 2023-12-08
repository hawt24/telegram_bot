from Controllers.BaseController import BaseController
from Models.Driver import Driver

class DriverController(BaseController):
    def __init__(self, html) -> None:
        super().__init__(html)
        self.driver = Driver()
    
    def menu_handler(self, message) -> None:
        self.driverJson = self.driver.menu(message.text)
        return self.driverJson