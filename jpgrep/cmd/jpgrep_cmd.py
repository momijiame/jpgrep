#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import click
from future.utils import text_type

from jpgrep.util import get_encoding
from jpgrep.util import filepathes
from jpgrep.util import FileObjectWrapper
from jpgrep.morpheme import StreamDetector


def _open(filepath):
    file = open(filepath, mode='rb')
    wrapper = FileObjectWrapper(file)
    return wrapper


def _executor(targets):
    for target in targets:
        if target.name.find('<std') == 0:
            # プロセスが異なると標準入出力が異なってしまうので
            return ThreadPoolExecutor()

    return ProcessPoolExecutor()


@click.command()
@click.option('-v', '--inverse', type=bool, is_flag=True)
@click.argument('query', type=text_type, nargs=1)
@click.argument('files', nargs=-1)
def cmd(inverse, query, files):

    targets = []

    # 処理対象のファイルがない場合は標準入力を検索対象にする
    if len(files) < 1:
        targets = [FileObjectWrapper(sys.stdin)]

    # 処理対象のファイルがある場合はバイナリモードでオープンする
    for file in files:
        relpathes = filepathes(file)
        file_objects = [_open(relpath) for relpath in relpathes]
        targets.extend(file_objects)

    executor = _executor(targets)
    with executor as e:
        mappings = dict((e.submit(_dispatch, target, query, inverse),
                         target)
                        for target in targets)
        for future in futures.as_completed(mappings):
            target = mappings[future]
            troves = future.result()

            for trove in troves:
                _print(target.name, trove.line)


def _print(name, line):
    if _is_stdio(name):
        print(line)
    else:
        path = os.path.relpath(name)
        msg = '{path}:{line}'.format(path=path, line=line)
        print(msg)


def _is_stdio(name):
    return name.find('<std') == 0


def _dispatch(target, query, inverse):
    detector = StreamDetector(query, inverse)
    with target.file as file:
        binary = file.read()

    encoding = get_encoding(binary)
    if encoding is None:
        # エンコードが不明 (おそらくバイナリファイルだった)
        return []

    text = binary.decode(encoding)
    # XXX: ファイルの改行コードも検出すべきだろうか？
    lines = text.split(os.linesep)

    troves = []
    for line in lines:
        trove = detector.feed(line)
        if trove is None:
            continue
        troves.append(trove)

    return troves


def main():
    cmd()


if __name__ == '__main__':
    main()
