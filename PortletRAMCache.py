# Copyright (c) 2003-2004 Chalmers University of Technology
# Authors: Jean-Marc Orliaguet <jmo@ita.chalmers.se>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

__author__ = "Jean-Marc Orliaguet <jmo@ita.chalmers.se>"

"""
  RAMCache
"""

import time
from thread import allocate_lock

class SimpleRAMCache:
    """Simple non-persistent RAM cache.
       Read / write / invalidate.
    """

    def __init__(self):
        self.cache = {}
        self.valid = 0
        self.last_update = 0
        self.writelock = allocate_lock()

    def getEntry(self, index=None):
        """Gets a cache entry by its index
           Returns None if the entry is not in the cache.
        """

        if not self.valid:
            return None
        data = None
        cache = self.cache
        if cache.has_key(index):
            data = cache[index]
        return data

    def setEntry(self, index=None, data=None):
        """Sets a cache entry."""

        self.writelock.acquire()
        try:
            if data is not None:
                self.cache[index] = data
                self.valid = 1
                self.last_update = time.time()
        finally:
            self.writelock.release()

    def getLastUpdate(self):
        """Gets the last update time"""

        return self.last_update

    def invalidate(self):
        """Invalidates the RAM cache."""

        self.writelock.acquire()
        try:
            for k in self.cache.keys():
                del self.cache[k]
            self.valid = 0
        finally:
            self.writelock.release()


class RAMCache:
    """Non-persistent RAM cache."""

    def __init__(self):
        self.cache = {}
        self.count = 0
        self.hits = 0
        self.misses = 0
        self.last_cleanup = {}
        self.valid = 0
        self.writelock = allocate_lock()

    def getEntry(self, index=None):
        """Gets a cache entry by its index
           Returns None if the entry is not in the cache.
        """

        if not self.valid:
            return None
        data = None
        cache = self.cache
        self.writelock.acquire()
        try:
            if cache.has_key(index):
                data = cache[index]
                self.hits += 1
            else:
                self.misses += 1
            self.count += 1
        finally:
            self.writelock.release()
        return data

    def setEntry(self, index=None, data=None):
        """Sets a cache entry."""

        if data is not None:
            self.writelock.acquire()
            try:
                self.cache[index] = data
                self.valid = 1
            finally:
                self.writelock.release()

    def delEntries(self, id=None):
        """Deletes entries."""

        self.writelock.acquire()
        try:
            for k in self.cache.keys():
                if k[0] == id:
                    del self.cache[k]
            self.last_cleanup[id] = time.time()
        finally:
            self.writelock.release()

    def getEntries(self):
        """Gets all the cache entries."""

        return self.cache.items()

    def getLastCleanup(self, id=None):
        """Gets the last cleanup time"""

        return self.last_cleanup.get(id, None)

    def invalidate(self):
        """Invalidates the RAM cache."""

        self.writelock.acquire()
        try:
            for k in self.cache.keys():
                del self.cache[k]
            self.count = 0
            self.hits = 0
            self.misses = 0
            for k in self.last_cleanup.keys():
                del self.last_cleanup[k]
            self.valid = 0
        finally:
            self.writelock.release()

    def calcsize(self, i, s=0):
        """Calculate the size of an object.
        """
        if isinstance(i, str):
            s = len(i)
        elif isinstance(i, dict):
            for k, v in i.items():
                s += self.calcsize(k)
                s += self.calcsize(v)
        elif isinstance(i, (list, tuple)):
            for v in i:
                s += self.calcsize(v)
        return s

    def getSize(self):
        """Returns the size of the cache."""

        return self.calcsize(self.cache)

    def getStats(self):
        """Returns statistics about the cache."""

        return {'count': self.count,
                'hits': self.hits,
                'misses': self.misses,
                'size': self.getSize(),
               }

    def getReport(self):
        """Returns a cache report."""

        stats_dict = {}
        for k, v in self.cache.items():
            size = self.calcsize(k) + self.calcsize(v)
            entry = k[0]
            if stats_dict.has_key(entry):
                stats_dict[entry]['count'] += 1
                stats_dict[entry]['size'] += size
            else:
                stats_dict[entry] = {'count': 1,
                                     'size': size}
        for entry in stats_dict.keys():
            stats_dict[entry]['last_cleanup'] = self.getLastCleanup(entry)
        return stats_dict
