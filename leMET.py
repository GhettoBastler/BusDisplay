#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import requests
from datetime import datetime, time, timedelta
from lxml import html


URL = 'https://services.lemet.fr/fr/horaires/ligne/{LIGNE}/direction/{DIRECTION}/arret/{NOM_ARRET}/{CODE_ARRET}'


def _get_raw_timetable(ligne, direction, nom_arret, code_arret):
    """
    Fetch the webpage containing the timetable for a given line at a given stop"""

    resp = requests.get(URL.format(LIGNE=ligne, DIRECTION=direction, NOM_ARRET=nom_arret, CODE_ARRET=code_arret))
    resp.raise_for_status()
    return resp.content


def _remove_whitespaces(string):
    """
    Remove the whitespaces at the begining and end of a string"""
    match = re.match('^\s*(.+?)\s*$', string)
    return match.group(1)


def _parse_page(page):
    """
    Extract times from the timetable webpage"""

    res = {}
    tree = html.fromstring(page)

    res['ligne'] = _extract_line_label(tree)
    res['arret'] = _extract_stop_name(tree)

    timesheet = _extract_timesheet(tree)

    # Extract table lines (for bus lines with multiple destinations)
    directions = []
    for elem in _extract_dir_line_elems(tree):
        direction_label = _extract_dir_label(elem)

        # Extracting times
        times = []
        for time in _extract_time_elems(elem):
            minutes, is_realtime = _extract_minutes(time)
            is_tad = _is_tad(minutes, timesheet)
            times.append(
                {
                    'minutes': minutes,
                    'temps_reel': is_realtime,
                    'TAD': is_tad,
                }
            )

        directions.append(
            {
                'direction': direction_label,
                'passages': times,
            }
        )

    res['directions'] = directions

    return res


def _is_tad(minutes, timesheet):
    """
    Match minutes to the closest entry in the timesheet to identify On Demand Service"""
    dt = datetime.now() + timedelta(minutes=minutes)
    _, tad = min(timesheet, key=lambda t: abs(dt - t[0]))
    return tad


def _extract_minutes(time):
    time_str = _remove_whitespaces(time.text)
    if '<1' in time_str:
        minutes = 0

    elif ':' in time_str:
        # Calculate minutes between now and the given time
        dt = datetime.strptime(time_str, '%H:%M')
        timedelta = datetime.combine(datetime.now(), dt.time()) - datetime.now()
        minutes = int((timedelta.total_seconds() % (3600 * 24)) // 60)
    else:
        minutes = int(time_str)

    is_realtime = 'is-realtime' in time.get('class').split(' ')
    res = (minutes, is_realtime)

    return res


def _extract_time_elems(elem):
    return elem.xpath('.//span[contains(@class, \'is-Schedule-Line-Directions-Item-Time-C2\')]')


def _extract_dir_label(elem):
    return _remove_whitespaces(elem.xpath('.//span[@class=\'is-Schedule-Line-Directions-Item-Label\']/text()')[0]).replace('Destination ', '')

    
def _extract_dir_line_elems(tree):
    return tree.xpath('//span[@class=\'is-Schedule-Line-Directions-Content\']')
    

def _extract_line_label(tree):
    return tree.xpath('//strong[@class=\'is-Line-Label\']/text()')[0]


def _extract_stop_name(tree):
    stop_name_str = tree.xpath('//div[contains(@class, \'is-Line-Info\') and contains(text(), \'Arrêt\')]/text()')[0]
    return _remove_whitespaces(stop_name_str).replace('Arrêt ', '')


def _extract_timesheet(tree):
    res = []
    for row in tree.xpath('//table[@id=\'is-StopPoint-Timesheet\']/tbody/tr'):
        hours = int(row.xpath('./th/text()')[0][:-1])
        for cell in row.xpath('.//span[@class=\'is-Timesheet-Passage-Item-C1\']'):
            minutes = int(cell.xpath('./span/text()')[0])
            tad = bool(cell.xpath('.//i[contains(@class, \'is-Icon-sim-TAD-PHONE\')]'))
            res.append((datetime.combine(datetime.now(), time(hours, minutes)), tad))

    return res


def get_next_buses(line_id, way, stop_id):
    """
    Returns the next two buses for a given line at a given stop in a given way ('OUTWARD' or 'RETURN')"""

    page = _get_raw_timetable(line_id, way, 'arret', stop_id)
    return _parse_page(page)
