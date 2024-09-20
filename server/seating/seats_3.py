"""
*** imperfect allocations:
+-----------+---------+--------+---------+--------+------------+
|   players |   total | wind   | table   | meet   | indirect   |
|-----------+---------+--------+---------+--------+------------|
|        16 |       0 |        |         |        |            |
|        20 |       0 |        |         |        |            |
|        24 |       0 |        |         |        |            |
|        28 |       0 |        |         |        |            |
|        32 |       0 |        |         |        |            |
|        36 |       0 |        |         |        |            |
|        40 |       0 |        |         |        |            |
|        44 |       0 |        |         |        |            |
|        48 |       0 |        |         |        |            |
|        52 |       0 |        |         |        |            |
|        56 |       0 |        |         |        |            |
|        60 |       0 |        |         |        |            |
|        64 |       0 |        |         |        |            |
|        68 |       0 |        |         |        |            |
|        72 |       0 |        |         |        |            |
|        76 |       0 |        |         |        |            |
|        80 |       0 |        |         |        |            |
|        84 |       0 |        |         |        |            |
|        88 |       0 |        |         |        |            |
|        92 |       0 |        |         |        |            |
|        96 |       0 |        |         |        |            |
|       100 |       0 |        |         |        |            |
|       104 |       0 |        |         |        |            |
|       108 |       0 |        |         |        |            |
|       112 |       0 |        |         |        |            |
|       116 |       0 |        |         |        |            |
|       120 |       0 |        |         |        |            |
|       124 |       0 |        |         |        |            |
+-----------+---------+--------+---------+--------+------------+
***
"""

seats = {
    16: [[[1, 2, 3, 16],
     [4, 5, 6, 7],
     [8, 9, 10, 11],
     [12, 13, 14, 15]],
     [[13, 6, 8, 3],
     [16, 14, 11, 5],
     [2, 7, 12, 9],
     [15, 1, 4, 10]],
     [[11, 4, 13, 2],
     [9, 15, 16, 6],
     [7, 8, 1, 14],
     [10, 3, 5, 12]]],

    20: [[[1, 2, 3, 20],
     [4, 5, 6, 7],
     [8, 9, 10, 11],
     [12, 13, 14, 15],
     [16, 17, 18, 19]],
     [[19, 14, 9, 4],
     [3, 8, 13, 18],
     [2, 12, 7, 17],
     [6, 1, 11, 16],
     [15, 10, 20, 5]],
     [[18, 11, 5, 12],
     [9, 16, 15, 2],
     [13, 20, 19, 6],
     [17, 3, 4, 10],
     [14, 7, 1, 8]]],

    24: [[[1, 10, 20, 24],
     [4, 8, 9, 18],
     [2, 12, 16, 17],
     [3, 5, 6, 23],
     [7, 11, 13, 14],
     [15, 19, 21, 22]],
     [[17, 6, 4, 7],
     [14, 1, 12, 15],
     [20, 23, 22, 9],
     [11, 21, 24, 2],
     [5, 10, 8, 19],
     [18, 16, 3, 13]],
     [[12, 9, 5, 11],
     [19, 13, 17, 20],
     [21, 3, 1, 4],
     [16, 22, 7, 10],
     [24, 18, 15, 6],
     [23, 2, 14, 8]]],

    28: [[[4, 5, 6, 28],
     [1, 11, 15, 27],
     [2, 13, 17, 20],
     [3, 8, 22, 25],
     [7, 14, 18, 23],
     [9, 10, 19, 26],
     [12, 16, 21, 24]],
     [[27, 21, 26, 22],
     [20, 24, 23, 25],
     [16, 28, 14, 19],
     [5, 2, 12, 15],
     [6, 17, 3, 9],
     [8, 7, 1, 4],
     [11, 18, 13, 10]],
     [[14, 20, 10, 1],
     [26, 12, 4, 13],
     [25, 9, 5, 18],
     [24, 27, 7, 6],
     [21, 19, 11, 3],
     [23, 22, 2, 16],
     [28, 15, 8, 17]]],

    32: [[[1, 2, 3, 32],
     [4, 5, 6, 7],
     [8, 9, 10, 11],
     [12, 13, 14, 15],
     [16, 17, 18, 19],
     [20, 21, 22, 23],
     [24, 25, 26, 27],
     [28, 29, 30, 31]],
     [[25, 23, 5, 8],
     [26, 30, 20, 18],
     [15, 32, 17, 29],
     [11, 19, 28, 6],
     [3, 12, 27, 22],
     [13, 1, 31, 16],
     [10, 14, 4, 2],
     [7, 24, 9, 21]],
     [[19, 27, 7, 31],
     [23, 15, 11, 3],
     [2, 26, 13, 5],
     [29, 18, 21, 10],
     [14, 8, 1, 20],
     [30, 4, 24, 17],
     [22, 28, 16, 9],
     [32, 6, 25, 12]]],

    36: [[[3, 4, 29, 32],
     [5, 8, 15, 16],
     [17, 20, 27, 28],
     [1, 6, 10, 33],
     [9, 13, 18, 22],
     [21, 25, 30, 34],
     [7, 12, 23, 26],
     [2, 19, 24, 35],
     [11, 14, 31, 36]],
     [[28, 35, 12, 6],
     [24, 11, 4, 18],
     [30, 16, 36, 23],
     [13, 31, 32, 21],
     [8, 33, 7, 25],
     [26, 10, 5, 3],
     [19, 9, 20, 1],
     [14, 27, 34, 29],
     [22, 15, 17, 2]],
     [[25, 5, 11, 19],
     [20, 21, 2, 10],
     [29, 7, 35, 13],
     [16, 18, 3, 12],
     [4, 36, 6, 27],
     [32, 22, 33, 14],
     [15, 30, 28, 24],
     [23, 17, 1, 31],
     [34, 26, 8, 9]]],

    40: [[[3, 5, 22, 25],
     [8, 23, 24, 40],
     [1, 7, 15, 19],
     [16, 18, 35, 38],
     [13, 21, 36, 37],
     [14, 20, 28, 32],
     [9, 12, 29, 31],
     [10, 11, 26, 34],
     [2, 6, 27, 33],
     [4, 17, 30, 39]],
     [[36, 1, 34, 4],
     [35, 9, 39, 22],
     [17, 8, 10, 14],
     [19, 33, 25, 37],
     [38, 32, 7, 11],
     [27, 30, 21, 23],
     [40, 15, 5, 16],
     [20, 24, 12, 6],
     [29, 28, 13, 18],
     [31, 26, 2, 3]],
     [[39, 37, 11, 24],
     [28, 4, 33, 5],
     [6, 3, 38, 36],
     [30, 31, 20, 15],
     [34, 27, 40, 9],
     [22, 13, 1, 8],
     [26, 35, 14, 21],
     [18, 2, 17, 7],
     [12, 16, 19, 10],
     [32, 25, 23, 29]]],

    44: [[[5, 6, 9, 11],
     [13, 21, 23, 34],
     [2, 16, 35, 38],
     [8, 17, 32, 42],
     [7, 19, 20, 25],
     [1, 18, 22, 28],
     [3, 14, 31, 37],
     [4, 24, 36, 43],
     [10, 15, 26, 33],
     [12, 27, 29, 41],
     [30, 39, 40, 44]],
     [[39, 26, 4, 14],
     [36, 28, 19, 8],
     [41, 9, 43, 15],
     [16, 12, 25, 24],
     [44, 11, 2, 10],
     [6, 33, 27, 23],
     [17, 1, 38, 20],
     [40, 7, 21, 29],
     [35, 5, 30, 31],
     [18, 32, 34, 3],
     [42, 22, 37, 13]],
     [[19, 40, 3, 22],
     [14, 41, 16, 6],
     [32, 37, 33, 7],
     [38, 30, 10, 21],
     [24, 42, 1, 39],
     [20, 34, 5, 36],
     [4, 13, 12, 2],
     [27, 44, 18, 26],
     [29, 43, 11, 17],
     [25, 8, 15, 35],
     [23, 31, 28, 9]]],

    48: [[[1, 5, 18, 48],
     [16, 17, 21, 34],
     [2, 32, 33, 37],
     [8, 19, 41, 44],
     [9, 12, 24, 35],
     [3, 25, 28, 40],
     [4, 6, 13, 27],
     [20, 22, 29, 43],
     [11, 36, 38, 45],
     [7, 15, 26, 46],
     [14, 23, 31, 42],
     [10, 30, 39, 47]],
     [[47, 40, 16, 11],
     [31, 43, 48, 24],
     [25, 13, 10, 36],
     [33, 38, 34, 3],
     [26, 41, 4, 29],
     [45, 9, 42, 20],
     [17, 18, 35, 22],
     [23, 21, 44, 30],
     [28, 7, 14, 5],
     [19, 2, 6, 1],
     [37, 39, 46, 12],
     [32, 27, 15, 8]],
     [[38, 35, 2, 28],
     [40, 1, 20, 15],
     [6, 44, 3, 18],
     [29, 37, 23, 16],
     [21, 48, 7, 13],
     [22, 34, 12, 19],
     [39, 45, 5, 32],
     [27, 14, 9, 10],
     [24, 33, 47, 4],
     [36, 31, 8, 17],
     [30, 26, 43, 25],
     [46, 42, 11, 41]]],

    52: [[[1, 16, 24, 27],
     [8, 9, 22, 29],
     [4, 13, 23, 28],
     [2, 15, 20, 31],
     [18, 33, 41, 44],
     [25, 26, 39, 46],
     [21, 30, 40, 45],
     [19, 32, 37, 48],
     [7, 10, 35, 50],
     [5, 12, 42, 43],
     [6, 11, 38, 47],
     [3, 14, 36, 49],
     [17, 34, 51, 52]],
     [[48, 36, 29, 21],
     [41, 1, 43, 15],
     [33, 47, 17, 37],
     [10, 6, 28, 22],
     [12, 31, 4, 19],
     [13, 50, 3, 34],
     [9, 18, 7, 32],
     [27, 23, 45, 39],
     [40, 44, 11, 5],
     [24, 49, 26, 35],
     [42, 51, 8, 25],
     [20, 52, 16, 30],
     [14, 2, 46, 38]],
     [[30, 25, 15, 6],
     [47, 42, 32, 23],
     [34, 38, 5, 16],
     [35, 37, 12, 9],
     [39, 21, 50, 17],
     [22, 4, 52, 33],
     [31, 24, 10, 11],
     [46, 43, 18, 20],
     [36, 19, 2, 51],
     [45, 7, 44, 14],
     [29, 3, 1, 26],
     [28, 48, 27, 41],
     [49, 40, 13, 8]]],

    56: [[[1, 28, 30, 56],
     [2, 7, 33, 43],
     [4, 5, 32, 34],
     [6, 11, 37, 47],
     [8, 9, 36, 38],
     [10, 15, 41, 51],
     [12, 13, 40, 42],
     [14, 19, 45, 55],
     [16, 17, 44, 46],
     [18, 23, 31, 49],
     [20, 21, 48, 50],
     [22, 27, 35, 53],
     [24, 25, 52, 54],
     [3, 26, 29, 39]],
     [[33, 51, 20, 25],
     [27, 54, 26, 28],
     [11, 40, 38, 10],
     [15, 44, 42, 14],
     [43, 53, 12, 17],
     [39, 49, 8, 13],
     [29, 47, 16, 21],
     [23, 52, 50, 22],
     [55, 1, 24, 37],
     [30, 3, 2, 32],
     [7, 36, 34, 6],
     [5, 31, 56, 41],
     [19, 46, 18, 48],
     [35, 45, 4, 9]],
     [[41, 12, 39, 11],
     [48, 22, 17, 30],
     [37, 35, 7, 8],
     [25, 38, 28, 2],
     [47, 20, 49, 19],
     [50, 14, 9, 40],
     [51, 24, 53, 23],
     [32, 42, 6, 1],
     [31, 4, 3, 33],
     [45, 16, 43, 15],
     [54, 18, 13, 44],
     [52, 34, 21, 26],
     [56, 29, 55, 27],
     [36, 10, 46, 5]]],

    60: [[[12, 29, 43, 47],
     [13, 27, 44, 54],
     [14, 28, 42, 56],
     [2, 23, 35, 51],
     [5, 17, 38, 52],
     [8, 20, 32, 45],
     [1, 25, 34, 58],
     [4, 16, 40, 59],
     [10, 19, 31, 50],
     [24, 36, 48, 60],
     [6, 15, 39, 57],
     [9, 21, 30, 46],
     [3, 26, 37, 53],
     [7, 18, 41, 55],
     [11, 22, 33, 49]],
     [[28, 40, 49, 5],
     [25, 33, 47, 9],
     [57, 32, 22, 13],
     [38, 12, 45, 18],
     [36, 56, 23, 10],
     [50, 42, 15, 3],
     [37, 60, 55, 16],
     [58, 11, 24, 44],
     [43, 59, 21, 7],
     [19, 53, 6, 41],
     [31, 8, 52, 29],
     [17, 39, 51, 1],
     [48, 34, 27, 2],
     [20, 30, 54, 4],
     [35, 46, 26, 14]],
     [[44, 7, 56, 15],
     [53, 2, 29, 40],
     [45, 6, 16, 33],
     [46, 4, 36, 17],
     [21, 54, 11, 42],
     [51, 37, 9, 19],
     [32, 48, 12, 26],
     [49, 10, 20, 39],
     [34, 55, 8, 28],
     [18, 47, 13, 35],
     [22, 58, 14, 38],
     [27, 5, 59, 31],
     [23, 57, 1, 30],
     [52, 24, 3, 43],
     [60, 41, 50, 25]]],

    64: [[[29, 42, 55, 64],
     [13, 16, 39, 58],
     [10, 23, 32, 61],
     [7, 26, 45, 48],
     [3, 30, 41, 52],
     [14, 19, 36, 57],
     [9, 20, 35, 62],
     [4, 25, 46, 51],
     [2, 31, 40, 53],
     [15, 18, 37, 56],
     [8, 21, 34, 63],
     [5, 24, 47, 50],
     [1, 28, 43, 54],
     [12, 17, 38, 59],
     [11, 22, 33, 60],
     [6, 27, 44, 49]],
     [[33, 59, 28, 6],
     [44, 54, 11, 17],
     [38, 60, 27, 1],
     [49, 43, 12, 22],
     [58, 32, 29, 7],
     [56, 34, 31, 5],
     [47, 53, 18, 8],
     [23, 48, 13, 42],
     [62, 36, 25, 3],
     [39, 64, 61, 26],
     [51, 41, 20, 14],
     [52, 9, 19, 46],
     [21, 50, 15, 40],
     [57, 4, 30, 35],
     [37, 63, 24, 2],
     [45, 55, 16, 10]],
     [[19, 10, 53, 44],
     [22, 15, 48, 41],
     [46, 8, 17, 55],
     [32, 6, 57, 31],
     [43, 13, 50, 20],
     [64, 38, 63, 25],
     [40, 14, 49, 23],
     [26, 3, 60, 37],
     [54, 47, 9, 16],
     [42, 51, 21, 12],
     [36, 61, 2, 27],
     [59, 29, 4, 34],
     [18, 11, 52, 45],
     [24, 1, 62, 39],
     [35, 5, 58, 28],
     [30, 7, 56, 33]]],

    68: [[[21, 24, 25, 33],
     [1, 31, 43, 53],
     [3, 41, 45, 50],
     [22, 27, 42, 62],
     [4, 5, 7, 13],
     [6, 35, 59, 65],
     [9, 15, 26, 49],
     [10, 17, 28, 51],
     [29, 30, 32, 44],
     [12, 34, 48, 61],
     [14, 19, 54, 64],
     [16, 20, 47, 63],
     [18, 39, 46, 57],
     [2, 23, 40, 55],
     [8, 37, 56, 68],
     [11, 36, 52, 67],
     [38, 58, 60, 66]],
     [[34, 38, 65, 15],
     [63, 2, 21, 59],
     [36, 64, 57, 9],
     [26, 8, 55, 18],
     [66, 56, 12, 10],
     [17, 11, 53, 24],
     [23, 25, 22, 31],
     [32, 16, 37, 6],
     [41, 7, 58, 20],
     [68, 13, 30, 52],
     [39, 43, 51, 42],
     [33, 44, 27, 1],
     [49, 61, 19, 5],
     [54, 4, 67, 29],
     [40, 45, 14, 60],
     [47, 62, 50, 48],
     [35, 46, 3, 28]],
     [[67, 60, 10, 35],
     [64, 47, 13, 26],
     [62, 18, 66, 16],
     [51, 68, 20, 46],
     [19, 6, 36, 58],
     [43, 12, 38, 22],
     [27, 65, 8, 3],
     [42, 63, 15, 4],
     [53, 54, 2, 56],
     [25, 55, 1, 11],
     [48, 57, 49, 45],
     [30, 59, 17, 23],
     [31, 28, 29, 37],
     [52, 9, 41, 34],
     [7, 50, 33, 39],
     [61, 32, 24, 14],
     [44, 21, 5, 40]]],

    72: [[[10, 36, 43, 72],
     [24, 34, 60, 67],
     [12, 19, 48, 58],
     [11, 23, 42, 69],
     [21, 35, 47, 66],
     [18, 45, 59, 71],
     [13, 16, 41, 70],
     [22, 37, 40, 65],
     [17, 46, 61, 64],
     [2, 6, 14, 20],
     [26, 30, 38, 44],
     [50, 54, 62, 68],
     [15, 31, 52, 53],
     [4, 5, 39, 55],
     [7, 28, 29, 63],
     [1, 3, 33, 56],
     [8, 25, 27, 57],
     [9, 32, 49, 51]],
     [[52, 57, 69, 61],
     [4, 21, 13, 9],
     [37, 33, 28, 45],
     [16, 58, 56, 39],
     [60, 59, 22, 38],
     [44, 49, 6, 24],
     [19, 55, 65, 3],
     [32, 15, 64, 34],
     [53, 18, 23, 26],
     [42, 47, 50, 5],
     [27, 7, 17, 43],
     [66, 2, 71, 29],
     [48, 68, 30, 1],
     [31, 51, 67, 41],
     [54, 72, 20, 25],
     [46, 62, 12, 11],
     [14, 70, 35, 36],
     [63, 10, 8, 40]],
     [[59, 63, 54, 48],
     [61, 40, 1, 62],
     [34, 66, 36, 17],
     [45, 29, 9, 19],
     [23, 20, 55, 28],
     [65, 12, 10, 42],
     [71, 4, 68, 31],
     [47, 52, 44, 7],
     [56, 27, 2, 22],
     [51, 26, 46, 8],
     [72, 11, 15, 6],
     [58, 41, 18, 60],
     [57, 67, 5, 21],
     [64, 14, 25, 13],
     [70, 50, 3, 32],
     [49, 38, 16, 37],
     [43, 69, 53, 33],
     [35, 39, 24, 30]]],

    76: [[[5, 30, 55, 75],
     [6, 9, 32, 33],
     [31, 34, 57, 58],
     [7, 8, 56, 59],
     [10, 40, 45, 76],
     [25, 35, 65, 70],
     [15, 20, 50, 60],
     [3, 12, 44, 46],
     [28, 37, 69, 71],
     [19, 21, 53, 62],
     [2, 13, 41, 49],
     [27, 38, 66, 74],
     [16, 24, 52, 63],
     [18, 22, 26, 39],
     [43, 47, 51, 64],
     [1, 14, 68, 72],
     [4, 11, 42, 48],
     [29, 36, 67, 73],
     [17, 23, 54, 61]],
     [[38, 68, 73, 28],
     [14, 2, 46, 40],
     [48, 3, 43, 13],
     [72, 69, 36, 25],
     [39, 65, 71, 27],
     [61, 50, 19, 22],
     [54, 41, 62, 45],
     [30, 31, 9, 7],
     [21, 15, 64, 52],
     [11, 44, 76, 47],
     [51, 60, 24, 17],
     [75, 58, 33, 8],
     [35, 67, 74, 26],
     [49, 10, 1, 42],
     [57, 5, 59, 6],
     [32, 55, 34, 56],
     [37, 16, 20, 29],
     [63, 53, 18, 23],
     [66, 70, 4, 12]],
     [[53, 27, 25, 54],
     [52, 4, 3, 50],
     [73, 59, 12, 15],
     [33, 49, 60, 67],
     [41, 6, 21, 36],
     [9, 23, 40, 37],
     [26, 51, 75, 1],
     [76, 29, 28, 2],
     [47, 18, 30, 14],
     [55, 39, 72, 43],
     [46, 61, 31, 66],
     [71, 56, 11, 16],
     [13, 19, 70, 57],
     [65, 62, 48, 34],
     [44, 7, 38, 20],
     [24, 42, 8, 35],
     [69, 45, 63, 32],
     [58, 74, 17, 10],
     [68, 64, 22, 5]]],

    80: [[[19, 56, 71, 80],
     [2, 21, 58, 73],
     [4, 23, 60, 75],
     [6, 25, 62, 77],
     [8, 27, 64, 79],
     [10, 29, 41, 66],
     [12, 31, 43, 68],
     [14, 33, 45, 70],
     [16, 35, 47, 72],
     [18, 37, 49, 74],
     [20, 39, 51, 76],
     [1, 22, 53, 78],
     [3, 24, 40, 55],
     [5, 26, 42, 57],
     [7, 28, 44, 59],
     [9, 30, 46, 61],
     [11, 32, 48, 63],
     [13, 34, 50, 65],
     [15, 36, 52, 67],
     [17, 38, 54, 69]],
     [[53, 68, 16, 37],
     [47, 62, 31, 10],
     [63, 7, 78, 26],
     [36, 48, 73, 17],
     [21, 80, 77, 52],
     [42, 67, 30, 11],
     [40, 65, 28, 9],
     [59, 74, 22, 3],
     [23, 79, 2, 54],
     [60, 45, 29, 8],
     [43, 58, 27, 6],
     [25, 41, 56, 4],
     [38, 50, 75, 19],
     [46, 71, 34, 15],
     [39, 55, 70, 18],
     [32, 69, 13, 44],
     [61, 76, 5, 24],
     [57, 1, 72, 20],
     [66, 51, 35, 14],
     [33, 49, 12, 64]],
     [[50, 11, 79, 36],
     [45, 13, 76, 30],
     [22, 77, 68, 5],
     [28, 42, 3, 71],
     [67, 78, 24, 39],
     [48, 57, 25, 2],
     [52, 61, 6, 29],
     [75, 46, 7, 32],
     [65, 10, 33, 56],
     [80, 54, 15, 43],
     [49, 40, 17, 34],
     [70, 16, 59, 31],
     [62, 8, 23, 51],
     [44, 53, 21, 38],
     [74, 63, 20, 35],
     [27, 66, 55, 12],
     [69, 14, 37, 60],
     [58, 19, 4, 47],
     [64, 73, 18, 1],
     [72, 9, 26, 41]]],

    84: [[[19, 66, 80, 84],
     [10, 24, 28, 47],
     [38, 52, 56, 75],
     [2, 4, 22, 79],
     [23, 30, 32, 50],
     [51, 58, 60, 78],
     [3, 33, 36, 74],
     [18, 31, 61, 64],
     [5, 8, 46, 59],
     [6, 70, 71, 82],
     [14, 15, 26, 34],
     [42, 43, 54, 62],
     [7, 11, 17, 69],
     [13, 35, 39, 45],
     [41, 63, 67, 73],
     [9, 48, 72, 77],
     [16, 21, 37, 76],
     [20, 44, 49, 65],
     [1, 27, 53, 68],
     [12, 29, 55, 81],
     [25, 40, 57, 83]],
     [[56, 71, 7, 72],
     [77, 17, 38, 22],
     [80, 23, 5, 3],
     [26, 83, 58, 41],
     [81, 67, 20, 1],
     [54, 2, 69, 27],
     [50, 45, 21, 66],
     [15, 84, 16, 35],
     [47, 9, 6, 60],
     [43, 28, 63, 44],
     [53, 39, 76, 57],
     [36, 46, 40, 14],
     [32, 62, 65, 19],
     [59, 61, 79, 52],
     [64, 42, 74, 68],
     [33, 51, 24, 31],
     [29, 25, 11, 48],
     [55, 82, 30, 13],
     [4, 75, 34, 37],
     [73, 10, 78, 49],
     [70, 18, 8, 12]],
     [[27, 3, 70, 28],
     [31, 56, 14, 55],
     [72, 57, 73, 8],
     [71, 13, 19, 9],
     [65, 69, 75, 43],
     [52, 34, 25, 32],
     [67, 22, 51, 46],
     [63, 20, 66, 33],
     [45, 64, 44, 29],
     [39, 78, 18, 23],
     [74, 79, 50, 11],
     [76, 38, 35, 5],
     [58, 54, 77, 40],
     [60, 80, 62, 53],
     [17, 16, 1, 36],
     [21, 68, 82, 2],
     [24, 6, 81, 4],
     [61, 7, 48, 10],
     [49, 26, 12, 30],
     [84, 59, 83, 42],
     [37, 41, 47, 15]]],

    88: [[[1, 28, 41, 46],
     [2, 27, 34, 53],
     [4, 25, 39, 48],
     [8, 21, 38, 49],
     [13, 16, 40, 47],
     [3, 26, 36, 51],
     [6, 23, 43, 44],
     [30, 57, 70, 75],
     [31, 56, 63, 82],
     [33, 54, 68, 77],
     [37, 50, 67, 78],
     [42, 45, 69, 76],
     [32, 55, 65, 80],
     [35, 52, 72, 73],
     [12, 17, 59, 86],
     [5, 24, 60, 85],
     [10, 19, 62, 83],
     [9, 20, 66, 79],
     [11, 18, 71, 74],
     [7, 22, 61, 84],
     [14, 15, 64, 81],
     [29, 58, 87, 88]],
     [[15, 49, 42, 18],
     [58, 62, 26, 7],
     [22, 11, 81, 68],
     [61, 59, 19, 14],
     [60, 87, 31, 2],
     [17, 66, 83, 16],
     [74, 75, 37, 54],
     [55, 36, 88, 4],
     [46, 8, 45, 25],
     [27, 41, 50, 6],
     [52, 39, 80, 69],
     [43, 3, 48, 1],
     [73, 13, 76, 20],
     [44, 47, 78, 71],
     [51, 40, 23, 10],
     [65, 29, 84, 33],
     [70, 79, 35, 56],
     [72, 32, 77, 30],
     [85, 64, 12, 21],
     [63, 86, 24, 9],
     [82, 34, 57, 67],
     [38, 53, 28, 5]],
     [[87, 4, 33, 62],
     [16, 61, 21, 63],
     [54, 71, 82, 41],
     [28, 60, 9, 64],
     [66, 14, 58, 23],
     [57, 2, 6, 38],
     [76, 77, 56, 39],
     [80, 73, 46, 49],
     [59, 65, 11, 26],
     [69, 84, 30, 36],
     [40, 1, 7, 55],
     [67, 35, 86, 31],
     [75, 78, 15, 22],
     [83, 70, 13, 24],
     [50, 5, 3, 45],
     [47, 48, 10, 27],
     [81, 72, 29, 37],
     [53, 12, 25, 42],
     [88, 43, 52, 8],
     [20, 44, 51, 17],
     [68, 85, 18, 19],
     [79, 74, 32, 34]]],

    92: [[[23, 46, 69, 92],
     [1, 24, 48, 72],
     [2, 25, 50, 75],
     [3, 26, 52, 78],
     [4, 27, 54, 81],
     [5, 28, 56, 84],
     [6, 29, 58, 87],
     [7, 30, 60, 90],
     [8, 31, 62, 70],
     [9, 32, 64, 73],
     [10, 33, 66, 76],
     [11, 34, 68, 79],
     [12, 35, 47, 82],
     [13, 36, 49, 85],
     [14, 37, 51, 88],
     [15, 38, 53, 91],
     [16, 39, 55, 71],
     [17, 40, 57, 74],
     [18, 41, 59, 77],
     [19, 42, 61, 80],
     [20, 43, 63, 83],
     [21, 44, 65, 86],
     [22, 45, 67, 89]],
     [[26, 51, 76, 2],
     [54, 69, 39, 15],
     [44, 84, 20, 64],
     [29, 85, 5, 57],
     [42, 60, 78, 18],
     [86, 13, 37, 50],
     [90, 68, 23, 22],
     [70, 47, 92, 24],
     [36, 48, 83, 12],
     [46, 80, 11, 35],
     [43, 81, 19, 62],
     [52, 89, 14, 38],
     [25, 49, 73, 1],
     [34, 67, 77, 10],
     [27, 53, 79, 3],
     [72, 56, 40, 16],
     [31, 61, 91, 7],
     [45, 21, 87, 66],
     [74, 65, 33, 9],
     [55, 4, 82, 28],
     [75, 58, 41, 17],
     [63, 71, 32, 8],
     [30, 59, 88, 6]],
     [[79, 18, 43, 61],
     [88, 23, 21, 67],
     [58, 5, 86, 30],
     [76, 17, 42, 59],
     [85, 20, 45, 65],
     [91, 22, 24, 46],
     [73, 57, 16, 41],
     [37, 12, 84, 49],
     [50, 74, 1, 26],
     [77, 2, 27, 52],
     [51, 87, 38, 13],
     [56, 83, 4, 29],
     [53, 14, 90, 39],
     [28, 3, 80, 54],
     [89, 6, 31, 60],
     [71, 92, 25, 48],
     [66, 75, 9, 34],
     [82, 19, 44, 63],
     [78, 10, 35, 68],
     [81, 11, 36, 47],
     [32, 62, 7, 69],
     [40, 15, 70, 55],
     [64, 8, 72, 33]]],

    96: [[[24, 48, 72, 96],
     [1, 26, 51, 76],
     [2, 27, 58, 73],
     [3, 25, 57, 77],
     [4, 33, 59, 90],
     [5, 35, 56, 94],
     [6, 46, 64, 87],
     [7, 44, 67, 83],
     [8, 31, 61, 95],
     [9, 29, 62, 91],
     [10, 43, 70, 92],
     [11, 41, 69, 88],
     [12, 47, 49, 85],
     [13, 45, 50, 81],
     [14, 32, 53, 75],
     [15, 34, 54, 79],
     [16, 28, 68, 82],
     [17, 30, 71, 86],
     [18, 36, 65, 93],
     [19, 38, 66, 89],
     [20, 37, 55, 80],
     [21, 39, 52, 84],
     [22, 42, 60, 78],
     [23, 40, 63, 74]],
     [[38, 53, 85, 20],
     [34, 57, 95, 4],
     [47, 65, 86, 7],
     [69, 83, 29, 17],
     [60, 94, 30, 9],
     [88, 67, 18, 39],
     [59, 72, 26, 3],
     [41, 62, 75, 22],
     [71, 93, 42, 11],
     [49, 73, 1, 25],
     [33, 74, 15, 52],
     [51, 80, 44, 12],
     [58, 91, 32, 5],
     [37, 19, 92, 64],
     [66, 6, 82, 45],
     [28, 90, 8, 63],
     [56, 2, 76, 24],
     [81, 21, 36, 54],
     [40, 68, 89, 10],
     [46, 84, 13, 48],
     [43, 79, 23, 61],
     [55, 78, 35, 14],
     [70, 87, 16, 31],
     [50, 77, 96, 27]],
     [[54, 86, 37, 23],
     [42, 61, 21, 72],
     [84, 69, 28, 19],
     [30, 18, 80, 70],
     [87, 14, 45, 51],
     [76, 20, 40, 62],
     [68, 8, 94, 41],
     [27, 1, 79, 59],
     [52, 13, 77, 32],
     [95, 16, 38, 67],
     [31, 89, 11, 60],
     [78, 24, 3, 49],
     [82, 22, 39, 53],
     [85, 66, 4, 44],
     [73, 55, 12, 34],
     [65, 5, 81, 46],
     [64, 17, 91, 36],
     [92, 7, 33, 58],
     [96, 75, 25, 56],
     [90, 9, 43, 71],
     [74, 50, 2, 26],
     [63, 10, 93, 29],
     [83, 15, 48, 47],
     [57, 88, 6, 35]]],

    100: [[[25, 50, 75, 100],
     [1, 10, 12, 22],
     [3, 5, 6, 11],
     [28, 30, 31, 36],
     [29, 33, 40, 43],
     [54, 58, 65, 68],
     [52, 69, 70, 74],
     [77, 94, 95, 99],
     [76, 85, 87, 97],
     [9, 42, 71, 88],
     [7, 41, 73, 89],
     [15, 45, 60, 80],
     [17, 46, 63, 84],
     [16, 48, 64, 82],
     [4, 27, 51, 78],
     [20, 35, 55, 90],
     [18, 49, 62, 81],
     [21, 38, 59, 92],
     [23, 39, 57, 91],
     [8, 44, 72, 86],
     [2, 26, 53, 79],
     [24, 37, 56, 93],
     [13, 34, 67, 96],
     [14, 32, 66, 98],
     [19, 47, 61, 83]],
     [[86, 88, 98, 77],
     [34, 25, 44, 41],
     [38, 57, 94, 20],
     [90, 78, 96, 95],
     [59, 66, 69, 50],
     [89, 72, 43, 5],
     [73, 87, 9, 40],
     [75, 3, 54, 27],
     [31, 29, 32, 37],
     [82, 63, 45, 19],
     [100, 79, 28, 52],
     [99, 67, 33, 10],
     [58, 92, 24, 35],
     [55, 93, 22, 39],
     [11, 2, 13, 23],
     [42, 8, 74, 85],
     [51, 1, 26, 76],
     [60, 83, 49, 17],
     [12, 6, 4, 7],
     [65, 53, 71, 70],
     [48, 62, 84, 15],
     [97, 68, 14, 30],
     [47, 64, 80, 18],
     [46, 61, 81, 16],
     [91, 21, 36, 56]],
     [[84, 7, 58, 31],
     [6, 17, 15, 2],
     [32, 56, 83, 9],
     [67, 86, 23, 29],
     [53, 12, 46, 94],
     [49, 52, 91, 13],
     [10, 16, 11, 8],
     [45, 48, 38, 34],
     [30, 80, 5, 55],
     [85, 65, 20, 25],
     [39, 18, 76, 72],
     [43, 97, 1, 64],
     [79, 99, 82, 75],
     [81, 77, 90, 92],
     [68, 22, 89, 26],
     [69, 28, 21, 87],
     [63, 70, 73, 59],
     [93, 14, 47, 51],
     [35, 36, 41, 33],
     [61, 98, 42, 4],
     [78, 19, 37, 71],
     [95, 40, 100, 60],
     [57, 74, 50, 54],
     [44, 96, 3, 62],
     [88, 24, 27, 66]]],

    104: [[[14, 61, 71, 104],
     [4, 18, 65, 75],
     [8, 22, 69, 79],
     [12, 26, 73, 83],
     [16, 30, 77, 87],
     [20, 34, 81, 91],
     [24, 38, 85, 95],
     [28, 42, 89, 99],
     [32, 46, 93, 103],
     [3, 36, 50, 97],
     [7, 40, 54, 101],
     [1, 11, 44, 58],
     [5, 15, 48, 62],
     [9, 19, 52, 66],
     [13, 23, 56, 70],
     [17, 27, 60, 74],
     [21, 31, 64, 78],
     [25, 35, 68, 82],
     [29, 39, 72, 86],
     [33, 43, 76, 90],
     [37, 47, 80, 94],
     [41, 51, 84, 98],
     [45, 55, 88, 102],
     [2, 49, 59, 92],
     [6, 53, 63, 96],
     [10, 57, 67, 100]],
     [[102, 69, 12, 59],
     [35, 78, 92, 45],
     [56, 103, 42, 9],
     [95, 48, 1, 34],
     [49, 82, 96, 39],
     [75, 28, 14, 85],
     [101, 91, 30, 44],
     [62, 76, 29, 19],
     [81, 24, 10, 71],
     [67, 20, 6, 77],
     [36, 83, 22, 93],
     [88, 74, 41, 31],
     [54, 68, 21, 11],
     [60, 13, 46, 3],
     [61, 94, 51, 4],
     [58, 72, 25, 15],
     [55, 65, 98, 8],
     [100, 86, 53, 43],
     [50, 7, 17, 64],
     [18, 79, 32, 89],
     [63, 2, 16, 73],
     [52, 5, 99, 38],
     [27, 84, 70, 37],
     [104, 90, 47, 57],
     [40, 87, 97, 26],
     [80, 33, 66, 23]],
     [[57, 96, 38, 35],
     [93, 71, 74, 28],
     [30, 88, 27, 49],
     [22, 41, 19, 80],
     [34, 92, 31, 53],
     [76, 37, 15, 18],
     [77, 12, 58, 55],
     [26, 45, 23, 84],
     [90, 44, 87, 5],
     [68, 29, 7, 10],
     [64, 25, 3, 6],
     [103, 60, 2, 21],
     [98, 95, 13, 52],
     [39, 100, 61, 42],
     [66, 85, 20, 63],
     [73, 54, 8, 51],
     [86, 1, 83, 40],
     [99, 56, 102, 17],
     [82, 101, 79, 36],
     [69, 50, 4, 47],
     [70, 89, 24, 67],
     [59, 16, 62, 81],
     [46, 104, 43, 65],
     [91, 9, 94, 48],
     [72, 14, 11, 33],
     [97, 75, 78, 32]]],

    108: [[[4, 5, 6, 108],
     [2, 13, 17, 20],
     [3, 8, 22, 25],
     [7, 14, 18, 23],
     [9, 10, 19, 26],
     [12, 16, 21, 24],
     [27, 31, 32, 33],
     [29, 40, 44, 47],
     [30, 35, 49, 52],
     [34, 41, 45, 50],
     [36, 37, 46, 53],
     [39, 43, 48, 51],
     [54, 58, 59, 60],
     [56, 67, 71, 74],
     [57, 62, 76, 79],
     [61, 68, 72, 77],
     [63, 64, 73, 80],
     [66, 70, 75, 78],
     [81, 85, 86, 87],
     [83, 94, 98, 101],
     [84, 89, 103, 106],
     [88, 95, 99, 104],
     [90, 91, 100, 107],
     [93, 97, 102, 105],
     [1, 28, 55, 82],
     [11, 38, 65, 92],
     [15, 42, 69, 96]],
     [[103, 22, 49, 76],
     [40, 45, 37, 38],
     [96, 86, 93, 83],
     [46, 27, 41, 43],
     [92, 99, 91, 94],
     [79, 78, 74, 77],
     [70, 73, 68, 54],
     [10, 11, 13, 18],
     [6, 17, 9, 3],
     [64, 65, 67, 72],
     [16, 19, 108, 14],
     [60, 71, 57, 63],
     [98, 90, 87, 84],
     [32, 39, 42, 29],
     [106, 104, 105, 101],
     [75, 21, 48, 102],
     [97, 100, 95, 81],
     [5, 12, 15, 2],
     [58, 55, 61, 62],
     [8, 1, 7, 4],
     [28, 34, 31, 35],
     [33, 44, 36, 30],
     [85, 82, 89, 88],
     [69, 59, 66, 56],
     [23, 25, 24, 20],
     [26, 107, 53, 80],
     [52, 50, 51, 47]],
     [[53, 32, 30, 41],
     [71, 75, 79, 61],
     [18, 6, 16, 1],
     [101, 92, 81, 103],
     [102, 106, 88, 98],
     [59, 57, 80, 68],
     [44, 48, 52, 34],
     [78, 56, 58, 73],
     [50, 36, 40, 42],
     [14, 26, 3, 5],
     [45, 33, 43, 28],
     [95, 84, 107, 86],
     [12, 66, 39, 93],
     [72, 60, 70, 55],
     [77, 69, 63, 67],
     [76, 74, 54, 65],
     [62, 8, 35, 89],
     [99, 87, 82, 97],
     [104, 96, 94, 90],
     [13, 9, 23, 15],
     [49, 47, 38, 27],
     [37, 64, 10, 91],
     [51, 46, 29, 31],
     [20, 108, 11, 22],
     [105, 83, 85, 100],
     [24, 4, 2, 19],
     [21, 7, 25, 17]]],

    112: [[[1, 36, 43, 68],
     [2, 35, 49, 62],
     [4, 33, 50, 61],
     [8, 29, 48, 63],
     [16, 21, 52, 59],
     [5, 32, 44, 67],
     [10, 27, 51, 60],
     [17, 20, 46, 65],
     [3, 34, 55, 56],
     [38, 73, 80, 105],
     [39, 72, 86, 99],
     [41, 70, 87, 98],
     [45, 66, 85, 100],
     [53, 58, 89, 96],
     [42, 69, 81, 104],
     [47, 64, 88, 97],
     [54, 57, 83, 102],
     [40, 71, 92, 93],
     [6, 31, 75, 110],
     [12, 25, 76, 109],
     [13, 24, 78, 107],
     [11, 26, 82, 103],
     [15, 22, 90, 95],
     [7, 30, 79, 106],
     [14, 23, 84, 101],
     [9, 28, 91, 94],
     [18, 19, 77, 108],
     [37, 74, 111, 112]],
     [[81, 108, 32, 9],
     [20, 110, 21, 79],
     [24, 92, 97, 17],
     [27, 78, 74, 14],
     [109, 80, 15, 26],
     [30, 96, 93, 11],
     [77, 75, 33, 8],
     [55, 60, 98, 91],
     [111, 39, 2, 76],
     [31, 10, 65, 50],
     [94, 95, 42, 73],
     [28, 84, 105, 13],
     [51, 112, 64, 4],
     [49, 90, 99, 66],
     [25, 86, 103, 16],
     [89, 100, 72, 43],
     [69, 46, 7, 34],
     [29, 62, 12, 53],
     [56, 59, 104, 85],
     [70, 45, 1, 3],
     [58, 5, 57, 36],
     [52, 63, 35, 6],
     [101, 37, 41, 88],
     [67, 48, 19, 22],
     [83, 106, 71, 44],
     [82, 38, 107, 40],
     [68, 102, 47, 87],
     [23, 54, 61, 18]],
     [[99, 94, 26, 19],
     [97, 44, 96, 38],
     [63, 56, 20, 25],
     [34, 11, 110, 83],
     [108, 85, 73, 46],
     [64, 14, 31, 55],
     [102, 91, 37, 45],
     [48, 9, 36, 71],
     [75, 81, 22, 23],
     [104, 49, 70, 89],
     [66, 6, 53, 2],
     [86, 107, 30, 15],
     [72, 3, 5, 47],
     [21, 50, 69, 24],
     [60, 7, 59, 1],
     [35, 79, 10, 77],
     [84, 40, 109, 42],
     [98, 13, 95, 32],
     [87, 61, 106, 58],
     [92, 101, 68, 51],
     [80, 76, 16, 29],
     [78, 41, 4, 111],
     [33, 52, 67, 12],
     [74, 17, 28, 82],
     [43, 103, 39, 90],
     [105, 88, 18, 27],
     [65, 8, 112, 54],
     [100, 93, 62, 57]]],

    116: [[[1, 39, 97, 116],
     [33, 38, 45, 83],
     [11, 41, 76, 87],
     [2, 4, 44, 81],
     [35, 52, 66, 80],
     [28, 55, 82, 98],
     [5, 19, 54, 86],
     [32, 57, 73, 112],
     [24, 72, 93, 95],
     [7, 14, 65, 96],
     [26, 49, 60, 113],
     [31, 68, 77, 78],
     [8, 29, 74, 107],
     [27, 51, 56, 100],
     [16, 75, 88, 91],
     [9, 20, 53, 110],
     [10, 63, 64, 105],
     [13, 70, 99, 106],
     [3, 15, 18, 23],
     [47, 50, 59, 67],
     [84, 89, 101, 109],
     [6, 12, 22, 58],
     [40, 42, 46, 102],
     [30, 90, 94, 104],
     [21, 25, 34, 43],
     [48, 61, 71, 111],
     [17, 79, 85, 108],
     [36, 62, 92, 115],
     [37, 69, 103, 114]],
     [[68, 60, 48, 51],
     [104, 114, 116, 70],
     [62, 112, 49, 72],
     [90, 102, 110, 85],
     [64, 106, 11, 65],
     [86, 80, 109, 18],
     [14, 107, 100, 71],
     [98, 1, 40, 2],
     [55, 87, 20, 6],
     [50, 27, 61, 76],
     [111, 10, 21, 54],
     [59, 23, 13, 7],
     [105, 95, 91, 31],
     [57, 101, 28, 52],
     [115, 93, 63, 37],
     [29, 56, 83, 99],
     [66, 97, 15, 8],
     [38, 92, 89, 17],
     [79, 32, 78, 69],
     [108, 30, 9, 75],
     [43, 103, 47, 41],
     [34, 46, 39, 84],
     [82, 45, 3, 5],
     [53, 81, 67, 36],
     [4, 16, 19, 24],
     [96, 94, 25, 73],
     [12, 88, 42, 77],
     [22, 35, 26, 44],
     [58, 74, 113, 33]],
     [[100, 84, 57, 30],
     [76, 34, 75, 59],
     [39, 18, 90, 93],
     [94, 116, 115, 64],
     [73, 113, 50, 63],
     [60, 8, 24, 14],
     [112, 22, 55, 11],
     [91, 111, 86, 103],
     [54, 82, 37, 68],
     [114, 71, 105, 1],
     [44, 48, 104, 42],
     [74, 26, 95, 97],
     [56, 21, 7, 88],
     [67, 9, 98, 16],
     [77, 28, 51, 62],
     [92, 96, 106, 32],
     [45, 36, 23, 27],
     [81, 110, 87, 19],
     [107, 65, 12, 66],
     [89, 78, 43, 13],
     [102, 53, 58, 29],
     [80, 33, 70, 79],
     [15, 108, 72, 101],
     [46, 83, 6, 4],
     [85, 40, 35, 47],
     [109, 31, 10, 38],
     [99, 2, 41, 3],
     [61, 52, 69, 49],
     [20, 5, 17, 25]]],

    120: [[[63, 74, 107, 111],
     [16, 46, 68, 113],
     [14, 71, 88, 112],
     [15, 72, 87, 102],
     [33, 34, 59, 89],
     [7, 9, 65, 90],
     [40, 70, 94, 110],
     [1, 54, 79, 80],
     [26, 67, 114, 120],
     [3, 18, 43, 98],
     [13, 57, 58, 118],
     [2, 48, 101, 117],
     [17, 76, 97, 99],
     [20, 21, 30, 44],
     [22, 25, 45, 81],
     [10, 11, 47, 78],
     [31, 32, 55, 108],
     [28, 53, 106, 109],
     [4, 24, 69, 104],
     [61, 85, 93, 95],
     [6, 56, 64, 83],
     [50, 52, 73, 75],
     [8, 42, 49, 86],
     [5, 19, 23, 119],
     [27, 51, 92, 96],
     [37, 66, 84, 116],
     [35, 38, 91, 103],
     [12, 39, 41, 60],
     [29, 62, 82, 100],
     [36, 77, 105, 115]],
     [[55, 13, 119, 106],
     [118, 43, 66, 20],
     [89, 109, 12, 45],
     [120, 28, 110, 68],
     [58, 111, 11, 87],
     [71, 103, 115, 50],
     [79, 98, 22, 34],
     [114, 91, 24, 2],
     [49, 36, 37, 29],
     [52, 113, 102, 4],
     [105, 30, 10, 73],
     [39, 95, 33, 27],
     [60, 116, 108, 38],
     [81, 23, 18, 54],
     [76, 31, 85, 42],
     [83, 7, 14, 8],
     [94, 1, 26, 82],
     [97, 65, 19, 88],
     [78, 112, 56, 48],
     [92, 44, 70, 63],
     [69, 86, 100, 25],
     [104, 101, 40, 62],
     [107, 6, 96, 53],
     [72, 59, 35, 57],
     [74, 99, 32, 77],
     [90, 17, 15, 51],
     [47, 41, 80, 21],
     [67, 84, 16, 3],
     [46, 117, 61, 9],
     [64, 5, 75, 93]],
     [[18, 110, 77, 14],
     [86, 27, 28, 12],
     [91, 10, 42, 15],
     [96, 40, 34, 31],
     [21, 120, 90, 16],
     [25, 35, 36, 84],
     [57, 100, 39, 64],
     [9, 88, 20, 52],
     [111, 79, 72, 69],
     [87, 94, 103, 33],
     [115, 75, 78, 104],
     [116, 73, 113, 49],
     [44, 37, 67, 11],
     [102, 8, 60, 76],
     [119, 105, 48, 46],
     [66, 58, 54, 26],
     [53, 2, 74, 19],
     [56, 118, 89, 70],
     [32, 22, 13, 23],
     [112, 107, 17, 43],
     [108, 93, 117, 41],
     [82, 63, 5, 65],
     [106, 29, 51, 71],
     [101, 114, 99, 6],
     [62, 80, 109, 24],
     [95, 47, 50, 55],
     [85, 4, 83, 1],
     [45, 61, 38, 7],
     [59, 68, 3, 92],
     [98, 97, 81, 30]]],

    124: [[[1, 40, 50, 73],
     [6, 35, 54, 69],
     [5, 36, 45, 78],
     [11, 30, 58, 65],
     [16, 25, 61, 62],
     [14, 27, 44, 79],
     [2, 39, 59, 64],
     [12, 29, 56, 67],
     [10, 31, 49, 74],
     [19, 22, 48, 75],
     [42, 81, 91, 114],
     [47, 76, 95, 110],
     [46, 77, 86, 119],
     [52, 71, 99, 106],
     [57, 66, 102, 103],
     [55, 68, 85, 120],
     [43, 80, 100, 105],
     [53, 70, 97, 108],
     [51, 72, 90, 115],
     [60, 63, 89, 116],
     [9, 32, 83, 122],
     [13, 28, 88, 117],
     [4, 37, 87, 118],
     [17, 24, 93, 112],
     [20, 21, 98, 107],
     [3, 38, 96, 109],
     [18, 23, 84, 121],
     [15, 26, 94, 111],
     [8, 33, 92, 113],
     [7, 34, 101, 104],
     [41, 82, 123, 124]],
     [[83, 93, 2, 10],
     [48, 46, 120, 97],
     [30, 99, 118, 23],
     [89, 87, 38, 15],
     [32, 117, 21, 100],
     [29, 90, 24, 86],
     [102, 3, 115, 9],
     [94, 19, 82, 34],
     [110, 107, 13, 40],
     [36, 17, 64, 71],
     [22, 67, 31, 68],
     [116, 101, 41, 53],
     [95, 122, 69, 66],
     [50, 44, 33, 20],
     [98, 14, 119, 39],
     [75, 60, 124, 12],
     [65, 8, 4, 70],
     [79, 5, 7, 56],
     [27, 104, 113, 26],
     [81, 54, 28, 25],
     [76, 114, 103, 59],
     [58, 112, 105, 77],
     [106, 49, 111, 45],
     [123, 88, 6, 47],
     [61, 85, 74, 91],
     [73, 18, 62, 35],
     [108, 109, 72, 63],
     [11, 51, 1, 43],
     [37, 55, 16, 80],
     [84, 92, 42, 52],
     [121, 57, 78, 96]],
     [[28, 108, 3, 87],
     [90, 105, 71, 42],
     [82, 113, 40, 32],
     [107, 12, 19, 88],
     [39, 91, 104, 33],
     [120, 13, 116, 18],
     [86, 78, 109, 76],
     [117, 119, 27, 4],
     [25, 6, 53, 60],
     [23, 83, 112, 8],
     [96, 2, 29, 99],
     [118, 123, 77, 36],
     [70, 43, 14, 17],
     [62, 7, 51, 24],
     [21, 106, 10, 89],
     [49, 64, 30, 1],
     [111, 58, 55, 84],
     [80, 74, 9, 22],
     [66, 94, 47, 101],
     [93, 16, 15, 102],
     [100, 79, 75, 95],
     [97, 61, 52, 98],
     [103, 48, 65, 92],
     [44, 69, 26, 5],
     [38, 59, 34, 54],
     [115, 121, 63, 50],
     [31, 124, 73, 81],
     [114, 41, 122, 72],
     [85, 110, 67, 46],
     [56, 20, 11, 57],
     [68, 45, 35, 37]]],

}