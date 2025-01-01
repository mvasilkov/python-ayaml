#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from pprint import pprint
from typing import Callable

import ayaml


def start(*, loads: Callable = ayaml.loads, exception: type[Exception] = ValueError):
    passed = 0
    failed = 0

    this_path = Path(__file__).parent.resolve()
    test_files = tuple(f for f in (this_path / 'json-test-suite' / 'test_parsing').glob('y_*.json') if f.is_file())

    for infile in test_files:
        print(f'{passed + failed + 1:4} │ {infile.stem}', end='... ')

        infile_text = infile.read_text(encoding='utf-8')

        try:
            infile_obj = loads(infile_text)
        except exception as err:
            print(f'Failed to parse YAML: {err}')
            print(f'In file: {infile.relative_to(this_path).as_posix()}')
            failed += 1
            continue

        try:
            jsonfile_obj = json.loads(infile_text)
        except json.decoder.JSONDecodeError as err:
            print(f'Failed to parse JSON: {err}')
            print(f'In file: {infile.relative_to(this_path).as_posix()}')
            continue

        if infile_obj[0] == jsonfile_obj:
            print('Passed')
            passed += 1
        else:
            print('Failed')
            failed += 1

            print(f'Expected: {infile.relative_to(this_path).as_posix()}')
            pprint(jsonfile_obj, indent=2)
            print(f'Got: {infile.relative_to(this_path).as_posix()}')
            pprint(infile_obj, indent=2)

    print(f'Passed: {passed}')
    print(f'Failed: {failed}')


if __name__ == '__main__':
    start()
