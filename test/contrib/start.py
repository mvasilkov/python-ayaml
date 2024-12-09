#!/usr/bin/env python3

from __future__ import annotations

from itertools import chain
import json
from pathlib import Path
from pprint import pprint
from typing import Callable

import ayaml


def json_loads(s: str) -> list:
    try:
        obj = None if s == '' else json.loads(s)
    except json.decoder.JSONDecodeError as err:
        if err.msg == 'Extra data':
            return json_loads_lines(s, err.pos)
        raise err

    return [] if s == '' else [obj]


def json_loads_lines(s: str, pos: int) -> list:
    part1 = s[:pos]
    part2 = s[pos:]

    return json_loads(part1) + json_loads(part2)


def title(test_dir: Path, this_path: Path) -> str:
    try:
        with (test_dir / '===').open(encoding='utf-8') as f:
            _title = f.readline().strip()
    except FileNotFoundError:
        _title = test_dir.relative_to(this_path).as_posix()

    return _title


def start(loads: Callable = ayaml.loads, exception: type[Exception] = ValueError):
    passed = 0
    failed = 0

    this_path = Path(__file__).parent.resolve()
    test_dirs = tuple(d for d in (this_path / 'yaml-test-suite').iterdir() if d.is_dir())
    test_dirs2 = (dd for dd in chain.from_iterable(d.iterdir() for d in test_dirs) if dd.is_dir())

    for test_dir in chain(test_dirs, test_dirs2):
        infile = test_dir / 'in.yaml'
        jsonfile = test_dir / 'in.json'
        if infile.is_file() and jsonfile.is_file():
            print(f'{passed + failed + 1:4} │ {title(test_dir, this_path)}', end='... ')

            infile_text = infile.read_text(encoding='utf-8')
            jsonfile_text = jsonfile.read_text(encoding='utf-8')

            try:
                infile_obj = loads(infile_text)
            except exception as err:
                print(f'Failed to parse YAML: {err}')
                print(f'In file: {infile.relative_to(this_path).as_posix()}')
                failed += 1
                continue

            try:
                jsonfile_obj = json_loads(jsonfile_text)
            except json.decoder.JSONDecodeError as err:
                print(f'Failed to parse JSON: {err}')
                print(f'In file: {jsonfile.relative_to(this_path).as_posix()}')
                continue

            if infile_obj == jsonfile_obj:
                print('Passed')
                passed += 1
            else:
                print('Failed')
                failed += 1

                print(f'Expected: {jsonfile.relative_to(this_path).as_posix()}')
                pprint(jsonfile_obj, indent=2)
                print(f'Got: {infile.relative_to(this_path).as_posix()}')
                pprint(infile_obj, indent=2)

    print(f'Passed: {passed}')
    print(f'Failed: {failed}')


if __name__ == '__main__':
    start()
