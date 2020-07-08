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

from appium.webdriver.webdriver import WebDriver as AppiumWebDriver

from src.testproject.enums import EnvironmentVariable
from src.testproject.helpers import ReportHelper, LoggingHelper, ConfigHelper
from src.testproject.rest import ReportSettings
from src.testproject.sdk.drivers.actions import WebActions
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers import CustomCommandExecutor
from src.testproject.sdk.internal.reporter import Reporter
from src.testproject.sdk.internal.session import AgentSession


class Remote(AppiumWebDriver):
    """Used to create a new Android driver instance

        Args:
            desired_capabilities (dict): Automation session desired capabilities and options
            projectname (str): Project name to report
            jobname (str): Job name to report
            disable_reports (bool): set to True to disable all reporting (no report will be created on TestProject)

        Attributes:
            _desired_capabilities (dict): Automation session desired capabilities and options
            _agent_client (AgentClient): client responsible for communicating with the TestProject agent
            _agent_session (AgentSession): stores properties of the current agent session
            command_executor (CustomCommandExecutor): the HTTP command executor used to send instructions to remote WebDriver
            w3c (bool): indicates whether or not the driver instance uses the W3C dialect
            session_id (str): contains the current session ID
    """

    def __init__(
        self,
        desired_capabilities: dict = None,
        token: str = None,
        projectname: str = None,
        jobname: str = None,
        disable_reports: bool = False,
    ):
        LoggingHelper.configure_logging()

        self._desired_capabilities = desired_capabilities

        self._token = token if token is not None else ConfigHelper.get_developer_token()

        if disable_reports:
            # Setting the project and job name to empty strings will cause the Agent to not initialize a report
            self._projectname = ""
            self._jobname = ""
        else:
            self._projectname = projectname if projectname is not None else ReportHelper.infer_project_name()
            self._jobname = jobname if jobname is not None else ReportHelper.infer_job_name()

        reportsettings = ReportSettings(self._projectname, self._jobname)

        self._agent_client: AgentClient = AgentClient(
            token=self._token, capabilities=self._desired_capabilities, reportsettings=reportsettings,
        )
        self._agent_session: AgentSession = self._agent_client.agent_session
        self.w3c = True if self._agent_session.dialect == "W3C" else False

        AppiumWebDriver.__init__(
            self, command_executor=self._agent_session.remote_address, desired_capabilities=self._desired_capabilities,
        )

        # Replace the standard command executor with our own to enable:
        # - automatic logging capabilities
        # - customized reporting settings
        self.command_executor = CustomCommandExecutor(
            agent_client=self._agent_client, remote_server_addr=self._agent_session.remote_address,
        )

    def start_session(self, capabilities, browser_profile=None):
        """Sets capabilities and sessionId obtained from the Agent when creating the original session."""
        self.session_id = self._agent_session.session_id
        logging.info(f"Session ID is {self.session_id}")

    def report(self) -> Reporter:
        """Enables access to the TestProject reporting actions from the driver object"""
        return Reporter(self.command_executor)

    def quit(self):
        """Quits the driver and stops the session with the Agent, cleaning up after itself."""
        try:
            AppiumWebDriver.quit(self)
        except Exception:
            pass

        # Stop the Agent client
        self.command_executor.agent_client.stop()

        # Clean up any environment variables set in the decorator
        for env_var in [
            EnvironmentVariable.TP_TEST_NAME,
            EnvironmentVariable.TP_PROJECT_NAME,
            EnvironmentVariable.TP_JOB_NAME,
        ]:
            EnvironmentVariable.remove(env_var)