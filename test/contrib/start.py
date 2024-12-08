#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from pprint import pprint

from ayaml import loads


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


def start():
    passed = 0
    failed = 0

    this_path = Path(__file__).parent.resolve()
    test_dirs = (d for d in (this_path / 'yaml-test-suite').iterdir() if d.is_dir())
    for test_dir in test_dirs:
        infile = test_dir / 'in.yaml'
        jsonfile = test_dir / 'in.json'
        if infile.is_file() and jsonfile.is_file():
            print(f'Running {test_dir.name}')

            infile_text = infile.read_text(encoding='utf-8')
            jsonfile_text = jsonfile.read_text(encoding='utf-8')

            try:
                infile_obj = loads(infile_text)
            except ValueError as err:
                print(f'Failed to parse YAML: {err}')
                failed += 1
                continue

            try:
                jsonfile_obj = json_loads(jsonfile_text)
            except json.decoder.JSONDecodeError as err:
                print(f'Failed to parse JSON: {err}')
                continue

            if infile_obj == jsonfile_obj:
                print('Passed')
                passed += 1
            else:
                print('Failed')
                failed += 1

                print('Expected:')
                pprint(jsonfile_obj, indent=2)
                print('Got:')
                pprint(infile_obj, indent=2)

    print(f'Passed: {passed}')
    print(f'Failed: {failed}')


if __name__ == '__main__':
    start()
