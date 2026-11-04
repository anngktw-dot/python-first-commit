#!/usr/bin/env python3
"""Квест «Хронологія»: сортування журналу та звірка складу.
Запуск: python3 analyze.py hub_log.txt inventory_recovered.txt
"""
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse
import csv
import re

TS = re.compile(r'(?<!\d)(2026-10-(?:13|14)T\d{2}:\d{2}:\d{2})\s*\|')
FIELDS = re.compile(r'([A-Za-z_]+)=([^|\s]+)')
START = datetime.fromisoformat('2026-10-13T23:00:00')
END = datetime.fromisoformat('2026-10-14T04:00:00')


def decode(path):
    raw = Path(path).read_bytes()
    for enc in ('utf-8-sig', 'utf-16', 'cp1251', 'latin1'):
        try:
            return raw.decode(enc), enc
        except UnicodeError:
            continue
    return raw.decode('utf-8', errors='replace'), 'utf-8 (replacement)'


def parse_log(text):
    entries, damaged = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        matches = list(TS.finditer(line))
        if not matches:
            if line.strip():
                damaged.append((lineno, line))
            continue
        if line[:matches[0].start()].strip():
            damaged.append((lineno, line[:matches[0].start()]))
        for i, match in enumerate(matches):
            ending = matches[i+1].start() if i+1 < len(matches) else len(line)
            segment = line[match.end():ending].strip()
            parts = segment.split('|')
            event = parts[0].strip() if parts else ''
            payload = '|'.join(parts[1:]).strip() if len(parts) > 1 else ''
            t = datetime.fromisoformat(match.group(1))
            if START <= t <= END:
                entries.append({
                    'time': t, 'event': event, 'payload': payload,
                    'line': lineno, 'raw': match.group(1) + '|' + segment
                })
            if not event or not payload:
                damaged.append((lineno, segment))
    entries.sort(key=lambda e: (e['time'], e['line']))
    return entries, damaged


def parse_inventory(text):
    rows = []
    for line in text.splitlines():
        if '|' not in line or line.lower().startswith('batch|'):
            continue
        cells = [c.strip() for c in line.split('|')]
        if len(cells) >= 7:
            rows.append(dict(zip(
                ('batch', 'name', 'category', 'qty', 'weight_kg', 'sector', 'status'),
                cells[:7]
            )))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('log', help='hub_log.txt')
    ap.add_argument('inventory', help='inventory_recovered.txt')
    args = ap.parse_args()
    log, log_enc = decode(args.log)
    inv, inv_enc = decode(args.inventory)
    events, damaged = parse_log(log)
    items = parse_inventory(inv)

    with open('хронологія_повна.txt', 'w', encoding='utf-8') as out:
        out.write('Хронологія 13.10 23:00 — 14.10 04:00, відсортована за повним часом\n')
        for e in events:
            out.write(f"{e['raw']}\n")

    with open('пошкоджені_рядки.txt', 'w', encoding='utf-8') as out:
        for ln, s in damaged:
            out.write(f'Рядок {ln}: {s}\n')

    cargo = [e for e in events if e['event'] == 'CARGO']
    with open('звірка_складу.csv', 'w', encoding='utf-8-sig', newline='') as out:
        wr = csv.writer(out)
        wr.writerow(['batch', 'inventory_sector', 'inventory_qty', 'inventory_status',
                     'log_time', 'log_action', 'log_gate', 'remark'])
        known = defaultdict(list)
        for e in cargo:
            k = dict(FIELDS.findall(e['payload']))
            if k.get('batch'):
                known[k['batch']].append((e, k))
        for item in items:
            records = known.get(item['batch'], [])
            for e, k in records or [(None, {})]:
                remark = 'Зіставлено запис' if records else 'Переміщення не знайдено у видимому журналі'
                wr.writerow([
                    item['batch'], item['sector'], item['qty'], item['status'],
                    e['time'].isoformat(sep=' ') if e else '',
                    k.get('action', ''), k.get('gate', ''), remark
                ])

    def match(event, **fields):
        return next((
            e for e in events
            if e['event'] == event and
            all(dict(FIELDS.findall(e['payload'])).get(k) == v for k, v in fields.items())
        ), None)

    disable = match('ALARM', action='disable')
    smoke = match('SENSOR', zone='C', type='smoke')
    batch = match('CARGO', batch='7-P', action='out')
    with open('підсумок_аналізу.txt', 'w', encoding='utf-8') as out:
        out.write(f'Розібрано подій: {len(events)}; рядків/фрагментів для ручної перевірки: {len(damaged)}; складських позицій: {len(items)}.\n')
        out.write(f'Кодування журналу: {log_enc}; інвентарю: {inv_enc}.\n')
        for label, a, b in [
            ('Від вимкнення сигналізації до диму C', disable, smoke),
            ('Від вивезення 7-P до диму C', batch, smoke)
        ]:
            if a and b:
                out.write(f'{label}: {b["time"] - a["time"]}\n')
        out.write('Звірку по кожній партії дивіться у звірка_складу.csv. Сам факт наявності партії у відновленому описі не доводить, що її вивезення незаконне: потрібні статус і контекст.\n')
    print('Створено: хронологія_повна.txt, пошкоджені_рядки.txt, звірка_складу.csv, підсумок_аналізу.txt')


if __name__ == '__main__':
    main()
