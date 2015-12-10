#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import sys
import pickle

import nose
from nose.tools.trivial import eq_
from nose.tools.trivial import ok_

from jpgrep.util import binary2unicode
from jpgrep.util import FileObjectWrapper
from jpgrep.util import ByteWrapper


class Test_binary2unicode(object):

    def test(self):
        """ バイト列をユニコード文字列に変換する """
        expect = u'吾輩は猫である'
        binary = expect.encode('utf-8')

        text = binary2unicode(binary)

        eq_(text, expect)


class Test_FileObjectWrapper(object):

    def test_str(self):
        """ パスからラッパーオブジェクトを作る """
        wrapper = FileObjectWrapper('/dev/null')

        eq_(wrapper.name, '/dev/null')

        with wrapper.file as f:
            f.read(1)

    def test_file(self):
        """ ファイルオブジェクトからラッパーオブジェクトを作る """
        f = open('/dev/null')
        wrapper = FileObjectWrapper(f)

        eq_(wrapper.name, '/dev/null')

        with wrapper.file as f:
            f.read(1)

    def test_std(self):
        """ sys.stdin からラッパーオブジェクトを作る """
        wrapper = FileObjectWrapper(sys.stdin)

        eq_(wrapper.name, '<stdin>')
        ok_(hasattr(wrapper.file, 'read'))

        with wrapper.file as _:
            pass

    def test_pickle(self):
        """ Pickle 化、非 Pickle 化する """
        wrapper = FileObjectWrapper('/dev/null')

        binary = pickle.dumps(wrapper)
        restored_object = pickle.loads(binary)

        eq_(restored_object.name, '/dev/null')

        with restored_object.file as f:
            f.read(1)

    def test_pickle_std(self):
        """ sts.stdin のラッパーオブジェクトの Pickle を確認する """
        wrapper = FileObjectWrapper(sys.stdin)

        binary = pickle.dumps(wrapper)
        restored_object = pickle.loads(binary)

        ok_(hasattr(restored_object.file, 'read'))

    def test_pickle_unicode_file(self):
        """ 文字列モードで開いたファイルからバイト列を取り出す """
        message = u'こんにちは、世界'
        file_ = io.StringIO(message)
        byte_wrapper = ByteWrapper(file_)
        file_wrapper = FileObjectWrapper(byte_wrapper)

        with file_wrapper.file as f:
            binary = f.read()

        expect = message.encode(encoding='utf-8')
        eq_(expect, binary)


class Test_ByteWrapper(object):

    def test(self):
        """ 文字列モードのファイルライクオブジェクトからバイト列を取り出す """
        message = u'こんにちは、世界'
        file_ = io.StringIO(message)
        wrapper = ByteWrapper(file_)

        with wrapper as f:
            data = f.read()

        expect = message.encode('utf-8')
        eq_(data, expect)


if __name__ == '__main__':
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
