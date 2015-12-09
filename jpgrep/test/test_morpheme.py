#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nose
from nose.tools.trivial import eq_

from jpgrep.morpheme import tokenize
from jpgrep.morpheme import StreamDetector


class Test_tokenize(object):

    def test(self):
        '''
        正常系: 文章が適切に形態素に分解される
        '''
        text = u'吾輩は猫である'
        expect = [u'吾輩', u'は', u'猫', u'で', u'ある']
        tokens = tokenize(text)

        eq_(tokens, expect)


class Test_StreamDetector(object):

    def test_success_hit(self):
        '''
        正常系: 形態素にもとづいて文章にマッチする
        '''
        query = u'吾輩'
        detector = StreamDetector(query)

        line = u'吾輩は猫である'
        trove = detector.feed(line)

        eq_(trove.line, line)
        eq_(trove.position, 0)

    def test_success_hit_tokens(self):
        '''
        正常系: 複数の形態素でも文章にマッチする
        '''
        query = u'は猫で'
        detector = StreamDetector(query)

        line = u'吾輩は猫である'
        trove = detector.feed(line)

        eq_(trove.line, line)
        eq_(trove.position, 2)

    def test_success_miss(self):
        '''
        正常系: 形態素にもとづいて文章にマッチしない
        '''
        query = u'輩'
        detector = StreamDetector(query)

        line = u'吾輩は猫である'
        trove = detector.feed(line)

        eq_(trove, None)


if __name__ == '__main__':
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
