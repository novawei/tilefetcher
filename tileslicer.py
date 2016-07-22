#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'Nova'

import maputil
import os
import sqlite3


SLICES_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'slices.db')


def get_slice(start, end):
    rs = None
    conn = sqlite3.connect(SLICES_DB_PATH)
    cur = conn.cursor()
    try:
        sql = 'SELECT x, y, z FROM slices WHERE ROWID>=%d AND ROWID<%d;' % (start, end)
        cur.execute(sql)
        rs = cur.fetchall()
    except Exception, e:
        print e
    finally:
        cur.close()
        conn.close()
    return rs


def clear_slices():
    conn = sqlite3.connect(SLICES_DB_PATH)
    cur = conn.cursor()
    try:
        sql = 'DELETE FROM slices;'
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print e
    finally:
        cur.close()
        conn.close()


def slice_tiles(lng1, lat1, lng2, lat2, z1, z2):
    count = 0
    for z in range(z1, z2+1):
        count += slice_tiles_z(lng1, lat1, lng2, lat2, z)
    return count


def slice_tiles_z(lng1, lat1, lng2, lat2, z):
    tile1 = maputil.get_tile(lng1, lat1, z)
    tile2 = maputil.get_tile(lng2, lat2, z)
    x1 = tile1[0]
    y1 = tile1[1]
    x2 = tile2[0]
    y2 = tile2[1]

    if x1 > x2 or y1 > y2:
        print 'left-bottom coordinate must not less than right-top coordinate'
        return

    count = 0

    conn = sqlite3.connect(SLICES_DB_PATH)
    cur = conn.cursor()
    try:
        sql = 'INSERT INTO slices VALUES (?, ?, ?);'
        for x in xrange(x1, x2+1):
            for y in xrange(y1, y2+1):
                count += 1
                cur.execute(sql, (x, y, z))
        conn.commit()
    except Exception, e:
        print e
    finally:
        cur.close()
        conn.close()

    return count


if __name__ == '__main__':
    '''
    ShanDong Province
    {"lng":114.467361,"lat":34.127447}, {"lng":122.985309,"lat":38.125886}
    '''
    clear_slices()
    slice_tiles_z(114.467361, 34.127447, 122.985309, 38.125886, 12)
