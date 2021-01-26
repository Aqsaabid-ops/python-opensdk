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

from src.testproject.enums import SleepTimingType, TakeScreenshotConditionType


class StepSettings:
    """Represents settings for automatic step reporting."""
    def __init__(self, sleep_time: int = 0, sleep_timing_type: SleepTimingType = None, timeout: int = -1,
                 invert_result: bool = False, always_pass: bool = False,
                 screenshot_condition: TakeScreenshotConditionType = TakeScreenshotConditionType.Failure):
        self.sleep_time = sleep_time
        self.sleep_timing_type = sleep_timing_type
        self.timeout = timeout
        self.always_pass = always_pass
        self.invert_result = invert_result
        self.screenshot_condition = screenshot_condition