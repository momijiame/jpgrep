#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from jpgrep.util import binary2unicode
from jpgrep.morpheme import StreamDetector


def detect(query, file):
    detector = StreamDetector(query)

    for binary_line in iter(file.readline, b''):
        unicode_line = binary2unicode(binary_line)
        trove = detector.feed(unicode_line)
        yield trove
