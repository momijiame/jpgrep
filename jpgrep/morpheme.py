#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple

from janome.tokenizer import Tokenizer


_TOKENIZER = Tokenizer()


def tokenize(text):
    '''
    ユニコード文字列を形態素に分解する
    '''
    return [token.surface for token in _TOKENIZER.tokenize(text)]


class Trove(namedtuple('Trove',
                       ['lineno', 'position', 'query', 'line'])):
    pass


class StreamDetector(object):
    '''
    一行ずつ形態素に分解しながらクエリと一致するか調べる
    '''

    def __init__(self, query, inverse=False):
        self.tokens = tokenize(query)
        self.inverse = inverse
        self._query = query
        self._lineno = 1

    def _match_morpheme(self, tokens):
        for index, expect_token in enumerate(self.tokens):
            target_token = tokens[index]
            if target_token != expect_token:
                return False
        return True

    def _find_morpheme(self, tokens):
        for index in range(len(tokens) - len(self.tokens) + 1):
            is_match = self._match_morpheme(tokens[index:])
            if not is_match:
                continue
            # トークン同士が一致するものが見つかったので場所を返す
            return index
        else:
            # 見つからなかった (break しなかった) ので誤検出として -1 を返す
            return -1

    def _find(self, line):
        # 先にざっくりと文字列のレベルで一致するか確認しておく
        position = line.find(self._query)
        if position == -1:
            return -1

        # それっぽいものが見つかったら構文解析器を使って詳しく調べる
        tokens = tokenize(line)
        index = self._find_morpheme(tokens)
        if index == -1:
            return -1

        return position

    def feed(self, line):
        position = self._find(line)

        if position == -1 and self.inverse:
            # inverse のときは見つからなかったときに Trove を返す必要がある
            # position は Trove を返しつつシンタックスハイライトが不要とわかるように None にしておく
            position = None

        if position == -1:
            return None

        return Trove(self._lineno, position, self._query, line)
