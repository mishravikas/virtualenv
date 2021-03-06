from __future__ import absolute_import, unicode_literals

import logging
import os
import sys
from uuid import uuid4

import pytest

from virtualenv.discovery.builtin import get_interpreter
from virtualenv.discovery.py_info import PythonInfo
from virtualenv.info import fs_supports_symlink
from virtualenv.util.path import Path
from virtualenv.util.six import ensure_text


@pytest.mark.skipif(not fs_supports_symlink(), reason="symlink not supported")
@pytest.mark.parametrize("case", ["mixed", "lower", "upper"])
def test_discovery_via_path(monkeypatch, case, tmp_path, caplog, session_app_data):
    caplog.set_level(logging.DEBUG)
    current = PythonInfo.current_system(session_app_data)
    core = "somethingVeryCryptic{}".format(".".join(str(i) for i in current.version_info[0:3]))
    name = "somethingVeryCryptic"
    if case == "lower":
        name = name.lower()
    elif case == "upper":
        name = name.upper()
    exe_name = "{}{}{}".format(name, current.version_info.major, ".exe" if sys.platform == "win32" else "")
    target = tmp_path / current.distutils_install["scripts"]
    target.mkdir(parents=True)
    executable = target / exe_name
    os.symlink(sys.executable, ensure_text(str(executable)))
    pyvenv_cfg = Path(sys.executable).parents[1] / "pyvenv.cfg"
    if pyvenv_cfg.exists():
        (target / pyvenv_cfg.name).write_bytes(pyvenv_cfg.read_bytes())
    new_path = os.pathsep.join([str(target)] + os.environ.get(str("PATH"), str("")).split(os.pathsep))
    monkeypatch.setenv(str("PATH"), new_path)
    interpreter = get_interpreter(core)

    assert interpreter is not None


def test_discovery_via_path_not_found(tmp_path, monkeypatch):
    monkeypatch.setenv(str("PATH"), str(tmp_path))
    interpreter = get_interpreter(uuid4().hex)
    assert interpreter is None
