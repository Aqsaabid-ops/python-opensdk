# Copyright 2020 TestProject (https://testproject.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import ChromeOptions
from tests.pageobjects.web import LoginPage, ProfilePage


@pytest.fixture
def simple_test():
    driver = webdriver.Chrome()

    driver.get("https://passport.alibaba.com/icbu_login.htm?spm=a2700.8293689.scGlobalHomeHeader.8.23f967afCiQ4wD&tracelog=hd_signin")

    driver.find_element_by_css_selector("#loginId").send_keys("khanminal317@gmail.com")
    driver.find_element_by_css_selector("#password1").send_keys("Aqsadear@123")
    driver.find_element_by_css_selector("#submit-btn").click()

    passed = driver.find_element_by_css_selector("#logout").is_displayed()

    print("Test passed") if passed else print("Test failed")

    driver.quit()

if __name__ == "__main__":
    simple_test()
