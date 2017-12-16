#!/usr/bin/env python
# coding:utf-8
import os
import sys
import logging
import traceback
from pprint import pprint

LOGGING_FORMATTER = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
formatter = logging.Formatter(LOGGING_FORMATTER)

logging.basicConfig(
    level=logging.DEBUG,
    format=LOGGING_FORMATTER,
    datefmt='%d %m %Y %H:%M:%S',
    filename='%s' % __file__.replace('.py', '.log'),
    filemode='a')

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
# set a format which is simpler for console use

console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

logging.debug('debug')
logging.info('info')
logging.warning('warning')
logging.error('error')
logging.exception('exp')

test_output = """Listing configured runners                          ConfigFile=/etc/gitlab-runner/config.toml
53ae3120409e                                        Executor=shell Token=fd0e38938715788fddf53fd4bed026 URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=ca92795aebd859dd162d5bad2d6c44 URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=c6df56d336f022460d649bde30146b URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=84c4e2fb2c8367f198f82021f0e774 URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=cb87eefa55c109e13a3a5215c23131 URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=0e79bcd1c9fef670335c14d6438e94 URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=8c9ce245fe789f041c38f9d427088e URL=https://repo.louislabs.com/
shell_runner                                        Executor=shell Token=a7d9354807e7629a0892a93477504a URL=https://repo.louislabs.com/
"""


print(test_output)

pattern=r'(?P<m_reg_name>.+?)\s+Executor=(?P<m_executor>.+?) Token=(?P<m_token>.{0,30}) URL=(?P<m_url>.+?)\s'

import re
ms = re.findall(pattern, test_output)

from pprint import pprint
pprint(ms)
