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
import logging
import os
import inspect

from src.testproject.enums import EnvironmentVariable, ReportNamingElement


class ReportHelper:
    """Provides helper functions used in reporting command, tests and steps"""

    @classmethod
    def infer_test_name(cls) -> str:
        """Tries to infer the test name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred test name (typically the test method name)
        """
        # Did we set the test name using our decorator?
        test_name_in_decorator = os.environ.get(EnvironmentVariable.TP_TEST_NAME.value)
        if test_name_in_decorator is not None:
            return test_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            return current_test_info.split(" ")[0].split("::")[1]
        else:
            # Try finding the right entry in the call stack, assuming that unittest is used
            logging.debug("Attempting to infer test name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Test)
            logging.debug(f"Inferred test name '{result}' from inspect.stack()")
            return result if result is not None else "Unnamed Test"

    @classmethod
    def infer_project_name(cls) -> str:
        """Tries to infer the project name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred project name (typically the folder containing the test file)
        """
        # Did we set the project name using our decorator?
        project_name_in_decorator = os.environ.get(EnvironmentVariable.TP_PROJECT_NAME.value)
        if project_name_in_decorator is not None:
            return project_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            path_to_test_file = current_test_info.split(" ")[0].split("::")[0]
            return path_to_test_file[0 : path_to_test_file.rfind("/")].replace("/", ".")  # noqa: E203
        else:
            # Try finding the right entry in the call stack, assuming that unittest is used
            logging.debug("Attempting to infer project name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Project)
            logging.debug(f"Inferred project name '{result}' from inspect.stack()")
            return result if result is not None else "Unnamed Project"

    @classmethod
    def infer_job_name(cls) -> str:
        """Tries to infer the job name from the information in the decorator or given to us by pytest or unittest

        Returns:
            str: The inferred job name (typically the test file name (without the .py extension)
        """
        # Did we set the job name using our decorator?
        job_name_in_decorator = os.environ.get(EnvironmentVariable.TP_JOB_NAME.value)
        if job_name_in_decorator is not None:
            return job_name_in_decorator

        current_test_info = os.environ.get("PYTEST_CURRENT_TEST")

        if current_test_info is not None:
            # we're using pytest
            path_to_test_file = current_test_info.split(" ")[0].split("::")[0]
            return path_to_test_file.split("::")[0].split("/")[-1].split(".py")[0]
        else:
            # Try finding the right entry in the call stack, assuming that unittest is used
            logging.debug("Attempting to infer job name using inspect.stack()")
            result = cls.__find_name_in_call_stack_for(ReportNamingElement.Job)
            logging.debug(f"Inferred job name '{result}' from inspect.stack()")
            return result if result is not None else "Unnamed Job"

    @classmethod
    def __find_name_in_call_stack_for(cls, element_to_find: ReportNamingElement) -> str:
        """Uses the current call stack to try and infer a project, job or test name

        Args:
            element_to_find (ReportNamingElement): the report naming element that we're looking for

        Returns:
            str: the inferred report naming element value
        """
        # stack is iterated over in reverse order for efficiency
        for frame in inspect.stack().__reversed__():
            if frame.function.startswith("test"):
                if element_to_find == ReportNamingElement.Test:
                    # return the current method name as the test name
                    return frame.function
                elif element_to_find == ReportNamingElement.Project:
                    path_elements = os.path.normpath(frame.filename).split(os.sep)
                    # return the folder name containing the current test file as the project name
                    return str(path_elements[-2])
                elif element_to_find == ReportNamingElement.Job:
                    path_elements = os.path.normpath(frame.filename).split(os.sep)
                    # return the current test file name minus the .py extension as the job name
                    return str(path_elements[-1]).split(".py")[0]
                else:
                    return None
        # return None if no function starting with 'test' was found in the call stack
        return None