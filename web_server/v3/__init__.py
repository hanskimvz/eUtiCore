# Copyright (c) 2025, Hans kim(hanskimvz@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
가스 미터 원격 모니터링 시스템 API 서버 v3

이 패키지는 가스 미터 원격 모니터링 시스템의 API 서버 버전 3을 구현합니다.
"""

__version__ = '3.0.0'
__author__ = 'Hans kim'
__email__ = 'hanskimvz@gmail.com'

# from .proc_api import proc_api, application
from .login import proc_login, proc_register, proc_logout
from .user import process_users, process_floating_user
from .device import process_devices
from .data_process import process_data
from .usage import process_usage
from .event import process_events
from .subscriber import process_subscribers
from .database import process_database

__all__ = [
    'proc_api',
    # 'application',
    'proc_login',
    'proc_register',
    'proc_logout',
    'process_users',
    'process_floating_user',
    'process_devices',
    'process_data',
    'process_usage',
    'process_events',
    'process_subscribers',
    'process_database'
] 