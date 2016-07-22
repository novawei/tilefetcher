#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'Nova'

import tileslicer
import os
import urllib2
import platform
import multiprocessing
import threading


TILES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tiles')
HOSTS = ["http://online0.map.bdimg.com/tile/",
         "http://online1.map.bdimg.com/tile/",
         "http://online2.map.bdimg.com/tile/",
         "http://online3.map.bdimg.com/tile/",
         "http://online4.map.bdimg.com/tile/"]


def get_tile_url(host, x, y, z):
    return '%s?qt=tile&style=pl&udt=20160722&x=%d&y=%d&z=%d' % (host, x, y, z)


def get_save_path(x, y, z):
    z_str = str(z)
    x_str = str(x)
    y_name = '%d.png' % y

    z_dir = os.path.join(TILES_DIR, z_str)
    if not os.path.exists(z_dir):
        os.mkdir(z_dir)
    x_dir = os.path.join(z_dir, x_str)
    if not os.path.exists(x_dir):
        os.mkdir(x_dir)
    y_file = os.path.join(x_dir, y_name)

    del z_str
    del x_str
    del y_name
    del z_dir
    del x_dir

    return y_file


def fetch_process(start, end, host):
    thread_count = 5
    page_size = (end-start)/thread_count
    page_start = start

    threads = []

    for i in xrange(0, thread_count):
        page_end = min(page_start+page_size, end)
        t = threading.Thread(target=fetch_thread, args=(page_start, page_end, host))
        t.start()
        threads.append(t)
        page_start += page_size

    for t in threads:
        t.join()


def fetch_thread(start, end, host):
    page_size = 20
    while start < end:
        try:
            page_end = min(start+page_size, end)
            rs = tileslicer.get_slice(start, page_end)
            for x, y, z in rs:
                url = get_tile_url(host, x, y, z)
                save_path = get_save_path(x, y, z)
                if os.path.exists(save_path):
                    os.remove(save_path)

                # print '*',
                f_in = urllib2.urlopen(url)
                with open(save_path, 'wb') as f_out:
                    f_out.write(f_in.read())

                del url
                del save_path
                del f_in

            start += page_size
            del page_end
            del rs
        except Exception, e:
            print e
            break


def reset_fetcher():
    tileslicer.clear_slices()


def start_fetch(tile_count):
    host_count = len(HOSTS)
    proc_count = host_count
    page_size = tile_count/proc_count
    start = 0
    for i in xrange(0, proc_count):
        end = min(start+page_size, tile_count)
        host = HOSTS[i % host_count]
        if platform.system() == 'Darwin':
            # mac os crash if multiprocessing is used, currently using threading instead
            t = threading.Thread(target=fetch_thread, args=(start, end, host))
            t.start()
        else:
            proc = multiprocessing.Process(target=fetch_process, args=(start, end, host))
            proc.start()
        start += page_size


def fetch_tiles_z(lng1, lat1, lng2, lat2, z):
    print 'reset fetcher...'
    reset_fetcher()
    print 'start slicer...'
    tile_count = tileslicer.slice_tiles_z(lng1, lat1, lng2, lat2, z)
    print 'tile count %d' % tile_count
    print 'start fetching...'
    start_fetch(tile_count)


def fetch_tiles(lng1, lat1, lng2, lat2, z1, z2):
    print 'reset fetcher...'
    reset_fetcher()
    print 'start slicer...'
    tile_count = tileslicer.slice_tiles(lng1, lat1, lng2, lat2, z1, z2)
    print 'tile count %d' % tile_count
    print 'start fetching...'
    start_fetch(tile_count)


if __name__ == '__main__':
    if not os.path.exists(TILES_DIR):
        os.mkdir(TILES_DIR)

    '''
    ShanDong Province
    {"lng":114.467361,"lat":34.127447}, {"lng":122.985309,"lat":38.125886}
    '''
    fetch_tiles_z(114.467361, 34.127447, 122.985309, 38.125886, 17)

