# Copyright Buildbot Team Members
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
from hashlib import new as new_hash
from random import Random


def seeded_range(seed, start, stop=None, step=1, extra=None):
    """
    A filter to produce deterministic random numbers.

    Produce a random item from range(start, stop[, step]), use the value and
    optional ``extra`` value to set the seed for the random number generator.

    Basic usage::

        ansible_fqdn|seeded_range(60)

        "hello"|seeded_range(1, 10, extra="world")
    """
    hashed_seed = new_hash('sha1')
    hashed_seed.update(seed)

    if extra is not None:
        hashed_seed.update(extra)

    hashed_seed = hashed_seed.digest()

    # We rely on randrange's interpretation of parameters
    return Random(hashed_seed).randrange(start, stop, step)


def proxies_from_env(ret):
    for env in ['http_proxy', 'https_proxy', 'no_proxy']:
        if env in os.environ:
            ret[env] = os.environ[env]
    return ret


class FilterModule(object):
    """
    Buildbot Infra specific filters
    """

    def filters(self):
        return {
            'seeded_range': seeded_range,
            'proxies_from_env': proxies_from_env
        }
