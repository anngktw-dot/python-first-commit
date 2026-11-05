"""Практична робота «Хронологія». Лише стандартна бібліотека Python."""
from pathlib import Path
from datetime import datetime
import math
import re

BASE = Path(__file__).resolve().parent
START = datetime(2026, 10, 13, 23)
END = datetime(2026, 10, 14, 4)
REQUIRED = {
    'SYSTEM': ['status'], 'ACCESS': ['zone', 'card', 'result'],
    'SENSOR': ['zone', 'type', 'value'], 'GATE': ['gate', 'action'],
    'CARGO': ['batch', 'action', 'gate'], 'ALARM': ['zone', 'action'],
    'CALL': ['source', 'note'],
}


def read_text(path):
    """Читає текст і відхиляє HTML, вебархіви та двійкові файли."""
    data = path.read_bytes()
    if data.startswith(b'bplist') or b'\x00' in data:
        raise ValueError(f'{path.name}: потрібен звичайний текст, а не вебархів.')
    text = data.decode('utf-8-sig')
    if re.search(r'<(?:!doctype\s+html|html\b|head\b|body\b|plist\b)', text, re.I):
        raise ValueError(f'{path.name}: збережіть вміст як текст UTF-8, не HTML.')
    return text


def parse_log(text):
    """Розбирає рядки; дублікати й проблеми зберігає для перевірки."""
    events = []          # Події з журналу
    problems = []        # Рядки, у яких є помилки
    seen = {}            # Уже знайдені записи для перевірки дублікатів
    duplicates = 0
    for number, raw in enumerate(text.splitlines(), 1):
        try:
            parts = raw.strip().split('|')
            if len(parts) < 3:
                raise ValueError('неповний або пошкоджений рядок')
            time = datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S')
            kind = parts[1]
            fields = {}
            for part in parts[2:]:
                key, value = part.split('=', 1)
                if not key or not value or key in fields:
                    raise ValueError('порожнє або повторене поле')
                fields[key] = value
            if kind in REQUIRED:
                missing = [key for key in REQUIRED[kind] if key not in fields]
                if missing:
                    raise ValueError('відсутні поля: ' + ', '.join(missing))
            if kind == 'SENSOR':
                value = float(fields['value'].replace(',', '.'))
                if not math.isfinite(value):
                    raise ValueError('некоректне числове значення датчика')
            signature = (time, kind, tuple(sorted(fields.items())))
            duplicate = signature in seen
            if duplicate:
                duplicates += 1
                problems.append(f'hub_log.txt:{number}: дублікат рядка {seen[signature]} | {raw!r}')
            else:
                seen[signature] = number
            if kind not in REQUIRED:
                problems.append(f'hub_log.txt:{number}: невідомий тип; не доказ події | {raw!r}')
            events.append({'time': time, 'kind': kind, 'fields': fields,
                           'line': number, 'raw': raw, 'duplicate': duplicate})
        except ValueError as error:
            problems.append(f'hub_log.txt:{number}: {error} | {raw!r}')
    return sorted(events, key=lambda event: event['time']), problems, duplicates


def parse_inventory(text):
    """Перевіряє всі сім полів, не доповнюючи відсутні дані."""
    rows = []           # Усі рядки опису складу
    problems = []       # Помилки в описі
    seen = set()        # Номери партій, які вже зустрічалися
    lines = text.splitlines()
    headers = ['batch', 'name', 'category', 'qty', 'weight_kg', 'sector', 'status']
    if not lines or lines[0].split('|') != headers:
        raise ValueError('inventory_recovered.txt: невідомий заголовок таблиці')
    for number, raw in enumerate(lines[1:], 2):
        parts = raw.split('|')
        errors = []
        if len(parts) != len(headers):
            errors.append(f'полів {len(parts)} замість 7')
        row = dict(zip(headers, parts))
        for key in headers:
            if not row.get(key):
                errors.append(f'відсутнє {key}')
        batch = row.get('batch', '')
        if batch and not re.fullmatch(r'\d+-[A-Za-zА-Яа-яІіЇїЄєҐґ]', batch):
            errors.append('некоректний номер партії')
        if batch in seen:
            errors.append('повторений номер партії')
        if batch:
            seen.add(batch)
        for key in ['qty', 'weight_kg']:
            try:
                value = row.get(key, '').replace(',', '.')
                if key == 'qty':
                    value = int(value)       # Кількість — ціле число
                else:
                    value = float(value)     # Вага може бути дробовою
                if value < 0 or not math.isfinite(value):
                    raise ValueError()
            except ValueError:
                errors.append(f'некоректне число {key}')
        for key, allowed in [('category', ['antibiotic', 'vitamin', 'vaccine', 'experimental']),
                             ('sector', ['A', 'B', 'C']),
                             ('status', ['на складі', 'відвантажено', 'згоріло'])]:
            if row.get(key) and row[key] not in allowed:
                errors.append(f'невідоме {key}: {row[key]}')
        row['line'] = number
        rows.append(row)
        if errors:
            problems.append(f'inventory_recovered.txt:{number}: {"; ".join(errors)} | {raw!r}')
    return rows, problems


def select_events(events, kind, **fields):
    """Знаходить події за типом і потрібними полями без дублікатів."""
    result = []
    for event in events:
        if event['kind'] != kind or event['duplicate']:
            continue  # Пропускаємо інші типи та повтори

        matches = True
        for key, value in fields.items():
            if event['fields'].get(key) != value:
                matches = False
                break

        if matches:
            result.append(event)
    return result


def describe(event):
    """Форматує подію разом із посиланням на рядок джерела."""
    mark = ' [ДУБЛІКАТ]' if event['duplicate'] else ''
    if event['kind'] not in REQUIRED:
        mark += ' [НЕВІДОМИЙ ТИП — потребує перевірки]'
    return (f"{event['time']:%d.%m.%Y %H:%M:%S} | {event['kind']} | "
            + ' | '.join(f'{key}={value}' for key, value in event['fields'].items())
            + f" | hub_log.txt:{event['line']}{mark}")


def interval(first, second):
    """Обчислює різницю між однозначно визначеними подіями."""
    if len(first) != 1 or len(second) != 1:
        return 'неможливо однозначно обчислити: подія відсутня або має кілька кандидатів'
    seconds = int((second[0]['time'] - first[0]['time']).total_seconds())
    if seconds < 0:
        return 'кінцева подія відбулася раніше за початкову'
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours} год {minutes} хв {seconds} с'


def compare_inventory(events, rows):
    """Зіставляє кожне вивезення з описом за точним номером партії."""
    report, conflicts = [], []
    for event in select_events(events, 'CARGO', action='out'):
        batch = event['fields']['batch']
        matches = [row for row in rows if row.get('batch') == batch]
        report.append(describe(event))
        if len(matches) != 1:
            report.append('Опис відсутній або номер партії неоднозначний.')
            continue
        row = matches[0]
        report.append(f"inventory_recovered.txt:{row['line']}: {row.get('name')}; "
                      f"категорія={row.get('category')}; кількість={row.get('qty')}; "
                      f"вага={row.get('weight_kg')}; сектор={row.get('sector')}; "
                      f"статус={row.get('status', 'відсутній')}")
        if row.get('status') in ['згоріло', 'на складі']:
            report.append('РОЗБІЖНІСТЬ: вивезення в журналі, але інший статус в описі.')
            conflicts.append((event, row))
        elif row.get('status') == 'відвантажено':
            report.append('Статус узгоджується з вивезенням.')
        else:
            report.append('Статус не дозволяє зробити висновок.')
    report += ['У журналі немає кількості, ваги, назви й категорії вантажу: звірити їх неможливо.',
               'Час складання опису, обсяг вивезення і повнота журналу невідомі; '
               'розбіжність записів не доводить, що вся партія була вивезена або що був підпал.']
    return report, conflicts


def write_reports(events, rows, problems, duplicates):
    """Створює хронологію, звірку, інтервали й короткий висновок."""
    # Залишаємо записи лише за ніч, яка нас цікавить.
    period = [event for event in events if START <= event['time'] <= END]

    # Із повної хронології окремо виділяємо важливі події.
    important = []
    for event in period:
        kind = event['kind']
        fields = event['fields']
        if kind in ['ACCESS', 'ALARM', 'GATE', 'CARGO', 'CALL']:
            important.append(event)
        elif fields.get('status') in ['night_mode', 'offline']:
            important.append(event)
        elif kind == 'SENSOR':
            value = float(fields['value'].replace(',', '.'))
            if fields['type'] == 'smoke' or value >= 38.5:
                important.append(event)
    alarm = select_events(period, 'ALARM', action='disable', zone='all')
    smoke = select_events(period, 'SENSOR', type='smoke')[:1]
    cargo = select_events(period, 'CARGO', action='out')
    requested = select_events(period, 'CARGO', batch='7-P')
    offline = select_events(period, 'SYSTEM', status='offline')
    pairs = [('Вимкнення сигналізації → перший запис диму', alarm, smoke),
             ('Вимкнення сигналізації → вивезення партії', alarm, cargo),
             ('Переміщення 7-P → перший запис диму', requested, smoke),
             ('Перший запис диму → offline', smoke, offline),
             ('Відкриття → закриття воріт №3', select_events(period, 'GATE', gate='3', action='open'),
              select_events(period, 'GATE', gate='3', action='close')),
             ('Дим у C → дим у B', select_events(period, 'SENSOR', type='smoke', zone='C')[:1],
              select_events(period, 'SENSOR', type='smoke', zone='B')[:1])]
    comparison, conflicts = compare_inventory(events, rows)
    for event, row in conflicts:
        if START <= event['time'] <= END:
            pairs.append((f"Вивезення {row['batch']} (розбіжність) → перший запис диму", [event], smoke))
    report = [
        'ХРОНОЛОГІЯ: 13.10.2026 23:00:00 — 14.10.2026 04:00:00 (межі включено)',
        f'Розібрано записів: {len(events)}; у періоді: {len(period)}; дублікатів: {duplicates}.',
        'Невідомі типи наведені для повноти, але не використані як докази.',
        'ПОВНА ХРОНОЛОГІЯ',
    ]
    for event in period:
        report.append(describe(event))
    report.extend(['', 'ВАЖЛИВІ ПОДІЇ'])
    for event in important:
        report.append(describe(event))
    report.extend(['', 'ЧАСОВІ ІНТЕРВАЛИ'])
    for label, first, second in pairs:
        report.append(f'{label}: {interval(first, second)}.')
    report += ['', 'ЗВІРКА З ОПИСОМ (усі вивезення, включно з подіями до 23:00)', *comparison,
               '', 'МЕЖІ ВИСНОВКІВ',
               '7-P не підміняється номером 7-Б: це різні ідентифікатори.',
               'BLUE-0417 зафіксована при вимкненні сигналізації й доступі до C; власник картки невідомий.',
               'Для воріт №3 записаний автомобіль BC7781TT, але зв’язок водія з карткою не доведений.',
               'Дим і зростання температури узгоджуються з пожежею; точний момент займання невідомий.',
               'suppressed підтверджує стан тривоги, але не встановлює причину приглушення.',
               'offline означає стан системи; фізичне вимкнення сервера та його причина не доведені.',
               'Після останнього запису немає даних до 04:00; це не доказ відсутності подій.']
    (BASE / 'хронологія.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
    (BASE / 'пошкоджені_рядки.txt').write_text('\n'.join(problems) + '\n', encoding='utf-8')
    sentences = []
    night = select_events(period, 'SYSTEM', status='night_mode')
    access = select_events(period, 'ACCESS', card='BLUE-0417', zone='C', result='granted')
    if len(night) == len(alarm) == len(access) == 1:
        sentences.append(f"Склад перейшов у нічний режим о {night[0]['time']:%H:%M:%S}, а після півночі "
                         f"карткою BLUE-0417 вимкнули сигналізацію о {alarm[0]['time']:%H:%M:%S} "
                         f"і отримали доступ до сектору C о {access[0]['time']:%H:%M:%S} "
                         f"(рядки журналу {night[0]['line']}, {alarm[0]['line']}, {access[0]['line']}).")
    if conflicts:
        event, row = conflicts[0]
        sentences.append(f"Найпідозріліша розбіжність стосується партії {row['batch']}: "
                         f"о {event['time']:%H:%M:%S} журнал фіксує її вивезення через ворота №"
                         f"{event['fields']['gate']} (рядок {event['line']}), "
                         f"але в описі вона має статус «{row['status']}» (рядок {row['line']}).")
        sentences.append(f"Від цього вивезення до першого запису диму минуло {interval([event], smoke)}, "
                         'проте точний час початку пожежі невідомий.')
    else:
        sentences.append('Достовірної розбіжності між вивезеннями й статусами опису не знайдено.')
    if smoke and len(offline) == 1:
        sentences.append(f"Перший дим зафіксовано о {smoke[0]['time']:%H:%M:%S} "
                         f"(рядок {smoke[0]['line']}), а через {interval(smoke, offline)} "
                         f"система перейшла в offline (рядок {offline[0]['line']}).")
    # Не підміняємо партію 7-P схожим номером 7-Б.
    has_requested_batch = bool(requested)
    for row in rows:
        if row.get('batch') == '7-P':
            has_requested_batch = True

    final_note = 'Ці записи потребують перевірки, але не доводять підпал або чиюсь провину; '
    if has_requested_batch:
        final_note += 'дані про партію 7-P слід розглядати окремо.'
    else:
        final_note += 'партія 7-P у журналі й описі відсутня.'
    sentences.append(final_note)
    (BASE / 'висновок.txt').write_text(' '.join(sentences) + '\n', encoding='utf-8')
    print(f'Готово: {len(period)} записів у періоді, {duplicates} дублікатів, '
          f'{len(problems)} рядків для перевірки, {len(conflicts)} розбіжностей.')
    for label, first, second in pairs:
        print(f'{label}: {interval(first, second)}')


def main():
    """Читає обидва джерела й запускає аналіз без їх зміни."""
    try:
        log_text = read_text(BASE / 'hub_log.txt')
        inventory_text = read_text(BASE / 'inventory_recovered.txt')
        events, log_problems, duplicates = parse_log(log_text)
        rows, inventory_problems = parse_inventory(inventory_text)
        write_reports(events, rows, log_problems + inventory_problems, duplicates)
    except (OSError, UnicodeError, ValueError) as error:
        print(f'Не вдалося виконати аналіз: {error}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
