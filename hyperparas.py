#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue April 20 2021

@author: Xiaoyu Lu
"""

# in db.py
THRES = 40 # control min length of doc displayed on the result page
THRES_MAX = 50 # control max length of doc displayed on the result page

# in app.py
DOC_PER_PAGE = 8
K = 20  # less than or equal to: [10000]
INDEX_NAME = "wapo_docs_50k_lf"
DEBUG_TOPIC_ID = 805
SHOW_REL = False # whether to show doc rel and score on result page