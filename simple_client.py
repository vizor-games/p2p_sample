#!/usr/bin/python

from __future__ import print_function

import libtorrent as lt
import time
import sys

from common import load_state, save_state, tune_session


def main(uri):
    session = lt.session()

    load_state('client.state', session)
    tune_session(session)

    session.listen_on(28155, 28155)

    session.add_dht_router("router.utorrent.com", 6881)
    session.add_dht_router("router.bittorrent.com", 6881)
    session.add_dht_router("dht.transmissionbt.com", 6881)
    session.add_dht_router("dht.aelitis.com", 6881)

    session.start_dht()
    #session.start_lsd()

    session.start_natpmp()
    session.start_upnp()

    magnet = 'magnet:?xt=urn:btih:%s' % (uri,)
    h = lt.add_magnet_uri(session, magnet, {'save_path': './download',
                                            'storage_mode': lt.storage_mode_t.storage_mode_allocate,
                                            'paused': False,
                                            'auto_managed': False,
                                            'duplicate_is_error': False })

    def show_alerts():
        alerts = session.pop_alerts()
        for alert in alerts:
            print('Alert: %s: %s' % (alert.what(), alert.message()))

    while (not h.is_seed()):
        s = h.status()

        print('State: %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s dht_announce:%s' % \
              (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
               s.num_peers, s.state, s.announcing_to_dht))

        show_alerts()
        time.sleep(1)

    show_alerts()
    save_state('client.state', session)
    print('Download complete: %s' % (h.name(),))


if __name__ == "__main__":
    main(sys.argv[1])
