#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
import libtorrent as lt

def tune_session(session):
    _settings = session.settings()

    # for i in dir(_settings):
    #     if not i.startswith('_'):
    #         print('%s = %s' % (i, getattr(_settings, i)))

    _settings.use_dht_as_fallback = False
    _settings.ssl_listen = 0
    _settings.lazy_bitfields = True
    _settings.connection_speed = 20
    _settings.no_connect_privileged_ports = False
    _settings.upnp_ignore_nonrouters = True
    _settings.dht_announce_interval = 30

    #_settings.active_tracker_limit = -1
    #_settings.active_dht_limit = -1
    #_settings.active_lsd_limit = -1
    _settings.mixed_mode_algorithm = lt.bandwidth_mixed_algo_t.prefer_tcp

    _settings.max_out_request_queue = 7000
    _settings.enable_outgoing_utp = False
    _settings.enable_incoming_utp = False
    _settings.use_parole_mode = True

    session.set_settings(_settings)

    _dht_settings = session.get_dht_settings()
    _dht_settings.ignore_dark_internet = False
    _dht_settings.restrict_routing_ips = False
    _dht_settings.restrict_search_ips = False
    _dht_settings.search_branching = 20

    session.set_dht_settings(_dht_settings)

    session.add_extension(lt.create_ut_pex_plugin)
    session.add_extension(lt.create_ut_metadata_plugin)
    session.add_extension(lt.create_metadata_plugin)
    session.add_extension(lt.create_smart_ban_plugin)

    alerts = [ #'all_categories',
               #'debug_notification',
               #'dht_log_notification',
              'dht_notification',
              'dht_operation_notification',
              'error_notification',
              'incoming_request_notification',
              'ip_block_notification',
              'peer_log_notification',
              'peer_notification',
              'performance_warning',
              'picker_log_notification',
              'port_mapping_log_notification',
              'port_mapping_notification',
              'progress_notification',
              'session_log_notification',
              'stats_notification',
              'status_notification',
              'storage_notification',
              'torrent_log_notification',
              'tracker_notification']

    mask = 0

    for k in alerts:
        mask |= int(lt.alert.category_t.names[k])

    session.set_alert_mask(mask)



def load_state(state_file, session):
    try:
        state = lt.bdecode(open(state_file).read())
        print('SAVED STATE:\%s' % (pprint.pformat(state),))
        session.load_state(state)
    except IOError, v:
        print('Unable to load saved state: %s' % (v,))


def save_state(state_file, session):
    open(state_file, 'w').write(lt.bencode(session.save_state(0x4)))
