import logging
import os
from os.path import isfile, join
from typing import List, Tuple

import pytest

from openwpm import task_manager
from openwpm.storage.sql_provider import SqlLiteStorageProvider
from openwpm.types import BrowserParams, ManagerParams

from . import utilities


class OpenWPMTest:
    NUM_BROWSERS = 1

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        """Create a tmpdir fixture to be used in `get_test_config`.

        Based on:
        https://mail.python.org/pipermail/pytest-dev/2014-April/002484.html
        """
        self.tmpdir = str(tmpdir)

    def visit(self, page_url, data_dir="", sleep_after=0):
        """Visit a test page with the given parameters."""
        manager_params, browser_params = self.get_config(data_dir)
        structured_provider = SqlLiteStorageProvider(manager_params["db"])
        manager = task_manager.TaskManager(
            manager_params,
            browser_params,
            structured_provider,
            logger_kwargs={"log_level_console": logging.DEBUG},
        )
        if not page_url.startswith("http"):
            page_url = utilities.BASE_TEST_URL + page_url
        manager.get(url=page_url, sleep=sleep_after)
        manager.close()
        return manager_params["db"]

    def get_test_config(
        self,
        data_dir: str = "",
        num_browsers: int = NUM_BROWSERS,
        display_mode: str = "headless",
    ) -> Tuple[ManagerParams, List[BrowserParams]]:
        """Load and return the default test parameters."""
        if not data_dir:
            data_dir = self.tmpdir
        manager_params, browser_params = task_manager.load_default_params(num_browsers)
        manager_params["data_directory"] = data_dir
        manager_params["log_directory"] = data_dir
        for i in range(num_browsers):
            browser_params[i]["display_mode"] = display_mode
        manager_params["db"] = join(
            manager_params["data_directory"], manager_params["database_name"]
        )
        return manager_params, browser_params

    def is_installed(self, cmd):
        """Check if a program is available via the standard PATH lookup."""
        path = os.environ["PATH"].split(os.pathsep)
        for d in path:
            candidate = join(d, cmd)
            if isfile(candidate) and os.access(candidate, os.X_OK):
                return True
        return False

    def assert_is_installed(self, cmd):
        assert self.is_installed(cmd), "Cannot find %s in your system" % cmd
