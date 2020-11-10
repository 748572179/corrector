#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Title   : 关键字法纠错
@File    : keyword_corrector.py
@Author  : Tian
@Time    : 2020/06/16 5:04 下午
@Version : 1.0
"""
import logging
import os
import re

import six

from utils.BKtree import BKTree

logger = logging.getLogger(__name__)
from utils.char_sim import CharFuncs
class KwdCorrectorConfig:
    prob_threshold = 0.7
    similarity_threshold = 0.55
    key_words_file = 'config\kwds_credit_report.txt'
    char_meta_file = 'config\char_meta.txt'

    @classmethod
    def from_dict(cls, json_object):
        config = KwdCorrectorConfig()
        for (key, value) in six.iteritems(json_object):
            config.__dict__[key] = value
        return config

def build_tree():
    tree = BKTree(KwdCorrectorConfig.key_words_file)
    tree.plant_tree()
    return tree

def load_key_words_dict():
    file = os.path.join(os.path.dirname(__file__),
                            KwdCorrectorConfig.key_words_file)
    with open(file,"rb") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
    return set(lines)

def regulation(text, errors):
    reg = list(text)
    error_chars = ''
    for err in errors:
        reg[err] = '(.)'
        error_chars += text[err]
    reg = '^' + ''.join(reg) + '$'
    return reg, error_chars

tree = build_tree()
key_words = load_key_words_dict()

def correct_al(texts, err_positions):
    results = []
    for text, err in zip(texts, err_positions):
        try:
            if text in key_words:
                results.append(text)
                continue

            # 根据编辑距离找到近似的关键词
            distance = len(err)
            if distance == len(text):
                distance = len(text) - 1
            k = tree.search(text, distance)  # ['未还本金','已还本金','还本金'，'宋某还本金']
            if not k:
                results.append(text)
                continue

            # 正则找到词中需要进一步匹配的字
            reg, origin = regulation(text, err)  # '^(.)还本(.)$'
            candidates = []  # ['未金','已金']
            for _k in k:
                reg = reg.replace('))',')\)')
                r = re.match(reg, _k)
                if not r:  # '还本金'，'宋某还本金'  被过滤
                    continue
                cnd = ''.join([r.group(i + 1) for i in range(len(err))])
                candidates.append(cnd)  # ['未金','已金']
            if not candidates:
                results.append(text)
                continue

            # 根据汉字笔画编码找到最终的正确字
            sims = []
            model = CharFuncs('./config/char_meta.txt')
            for cnd in candidates:
                sims.append(model.shape_similarity(origin, cnd))  # [0.58, 0.30]
            if max(sims) < KwdCorrectorConfig.similarity_threshold:
                results.append(text)
                continue

            # 最终进行替换
            substitution = list(candidates[sims.index(max(sims))])  # ['未', '金']
            _t = list(text)
            for c in err:
                _t[c] = substitution.pop(0)
            results.append(''.join(_t))

        except Exception:
            results.append(text)
            import traceback
            logger.error(traceback.format_exc())

    return results

