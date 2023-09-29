# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 12:14:03 2023

@author: Alessandro Pieruzzi
"""

import os

listf = os.listdir(os.getcwd())
listf = [file[:-5] for file in listf if file.endswith('.xlsx') and not file.startswith('~')]



