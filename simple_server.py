#!/usr/bin/python

from __future__ import print_function

import libtorrent as lt
import time
import sys
import os

from common import load_state, save_state, tune_session

def make_torrent(update_dir):
    fs = lt.file_storage()
    lt.add_files(fs, os.path.join(os.getcwd(), 'upload/%s' % (update_dir,)))

    t = lt.create_torrent(fs)
    t.set_creator('server example')
    lt.set_piece_hashes(t, os.path.join(os.getcwd(), 'upload'))

    contents = t.generate()

    from pprint import pprint
    pprint(dict(contents))

    return lt.torrent_info(contents)


def main(update_dir):
    session = lt.session()

    load_state('server.state', session)
    tune_session(session)

    session.listen_on(28136, 28136)

    session.add_dht_router("router.utorrent.com", 6881)
    session.add_dht_router("router.bittorrent.com", 6881)
    session.add_dht_router("dht.transmissionbt.com", 6881)
    session.add_dht_router("dht.aelitis.com", 6881)

    session.start_dht()
    #session.start_natpmp()
    #session.start_upnp()
    session.start_lsd()

    torrent_info = make_torrent(update_dir)

    h = session.add_torrent({'ti': torrent_info, 'save_path': 'upload',
                             'storage_mode': lt.storage_mode_t.storage_mode_allocate,
                             'paused': False,
                             'auto_managed': False,
                             'duplicate_is_error': False })


    print('========\nHash is: %s\n========' % (torrent_info.info_hash()))
    print('Start: ', h.name())

    while True:
        s = h.status()

        print('State: %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s dht_announce:%s' % \
              (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
               s.num_peers, s.state, s.announcing_to_dht))

        alerts = session.pop_alerts()
        for alert in alerts:
            print('Alert: %s: %s' % (alert.what(), alert.message()))

        save_state('server.state', session)
        time.sleep(1)

    print(h.name(), '\ncomplete')


if __name__ == "__main__":
    main(sys.argv[1])
