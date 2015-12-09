#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import os
import io

import chardet


def binary2unicode(binary):
    '''
    バイト列から文字コードを検出した上でユニコード文字列にして返す
    '''
    encoding = get_encoding(binary)

    if encoding is None:
        # 文字コードが分からなかったのでデコード不能
        msg = 'can not decode since unknown encoding: {binary}'.format(binary=binary)  # noqa
        raise ValueError(msg)

    unicode_text = binary.decode(encoding)
    return unicode_text


def get_encoding(binary):
    '''
    バイト列から文字コードを検出する
    '''
    # 文字コード検出ライブラリを使ってちゃんと調べる
    encoding = _get_encoding_chardet(binary)
    if encoding is not None:
        return encoding

    # それでも分からなかったらお手上げ (きっとバイナリ)
    return None


def _get_encoding_chardet(binary):
    encoding_info = chardet.detect(binary)
    encoding = encoding_info.get('encoding')
    return encoding


def filepathes(path):
    '''
    パスに含まれるファイルの一覧をリストで返す
    '''
    is_directory = os.path.isdir(path)
    pathes = _dir_files(path) if is_directory else [path]

    return list(pathes)


def _dir_files(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


class FileObjectWrapper(object):
    """
    ファイル名、ファイルオブジェクト、標準入力を同様に扱えるようにしたラッパークラス
    Pickle 対応
    """

    def __init__(self, f):
        self._file = None

        if isinstance(f, str):
            # str
            self.name = f
            return

        if hasattr(f, 'name'):
            # maybe file object
            self.name = f.name
            return

        if isinstance(f, (ByteWrapper, io.StringIO)):
            # 純粋なテスト用なので Pickle 化を考慮していない
            self.name = None
            self._file = f
            return

        msg = 'Invalid argument: {f}'.format(f=f)
        raise ValueError(msg)

    @property
    def file(self):
        if self._file is None:
            self._open()

        return self._file

    def _open(self):
        if self.name.find('<std') == 0:
            attr_name = self.name[1:-1]
            fileobject = getattr(sys, attr_name)
            # sys.std* はユニコード文字列を返すので io.TextWrapper を使っているのでバイト列に直す
            self._file = ByteWrapper(fileobject)
        else:
            self._file = open(self.name, mode='rb')

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_file']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._file = None

    def __str__(self):
        class_name = self.__class__.__name__
        msg = '<{class_} name=\'{name}\'>'.format(class_=class_name,
                                                  name=self.name)
        return msg


class ByteWrapper(object):

    def __init__(self, fileobject):
        self.fileobject = fileobject

    def _encoding(self):
        if self.fileobject.encoding is not None:
            return self.fileobject.encoding

        # ファイルにエンコーディングの情報がないときは便宜的に UTF-8 でエンコードしておく
        return 'UTF-8'

    def read(self, n=None):
        data = self.fileobject.read(n)
        return data.encode(self._encoding())

    def __getatt__(self, name):
        return getattr(self.fileobject, name)

    def __enter__(self):
        self.fileobject.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.fileobject.__exit__(exc_type, exc_value, traceback)

    def __str__(self):
        return self.fileobject.__str__()
