# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Mu-L/cx_Freeze/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                  |    Stmts |     Miss |      Cover |   Missing |
|-------------------------------------- | -------: | -------: | ---------: | --------: |
| cx\_Freeze/\_\_init\_\_.py            |       52 |        0 |    100.00% |           |
| cx\_Freeze/\_\_main\_\_.py            |        4 |        0 |    100.00% |           |
| cx\_Freeze/\_compat.py                |       16 |        0 |    100.00% |           |
| cx\_Freeze/\_importlib.py             |        6 |        0 |    100.00% |           |
| cx\_Freeze/\_pyproject.py             |       20 |        0 |    100.00% |           |
| cx\_Freeze/bases/\_\_init\_\_.py      |        0 |        0 |    100.00% |           |
| cx\_Freeze/cli.py                     |       99 |        5 |     94.95% |233-236, 250, 262 |
| cx\_Freeze/command/\_\_init\_\_.py    |        0 |        0 |    100.00% |           |
| cx\_Freeze/command/\_pydialog.py      |       21 |        1 |     95.24% |        85 |
| cx\_Freeze/command/bdist\_appimage.py |      160 |       29 |     81.88% |92-96, 113, 119-125, 140-141, 159-172, 189, 194, 219, 277-278, 287-289, 294, 302, 309, 313 |
| cx\_Freeze/command/bdist\_deb.py      |       65 |       15 |     76.92% |48-52, 57-58, 83-86, 94, 105-114, 120-121 |
| cx\_Freeze/command/bdist\_dmg.py      |      189 |       20 |     89.42% |179-180, 194-198, 217, 222, 230, 263, 289, 291, 372-381 |
| cx\_Freeze/command/bdist\_mac.py      |      209 |      100 |     52.15% |166-170, 191-192, 220-247, 254, 256, 260, 264-286, 295, 306-313, 321, 362, 368, 375-384, 393, 410-424, 444-461, 464-482, 485-487, 490-529 |
| cx\_Freeze/command/bdist\_msi.py      |      418 |       27 |     93.54% |150, 157, 251-252, 675-676, 679, 682, 991-992, 995-1003, 1019, 1047-1052, 1055-1060, 1082, 1136, 1140, 1184-1185 |
| cx\_Freeze/command/bdist\_rpm.py      |      233 |       46 |     80.26% |206-210, 215-216, 236-239, 271-275, 279, 299, 319-323, 352-354, 406, 423, 443-444, 452, 455, 458, 461, 507-508, 523, 526-527, 536-550 |
| cx\_Freeze/command/build\_exe.py      |      115 |       48 |     58.26% |161-163, 167-196, 238-243, 247-248, 270, 323-332, 337 |
| cx\_Freeze/command/install.py         |       51 |        0 |    100.00% |           |
| cx\_Freeze/command/install\_exe.py    |       42 |        1 |     97.62% |        76 |
| cx\_Freeze/common.py                  |       67 |       27 |     59.70% |27, 34, 62, 66-67, 69-70, 75-76, 79-80, 98-119 |
| cx\_Freeze/darwintools.py             |      366 |      124 |     66.12% |34, 141, 145-155, 178-180, 184-213, 239-240, 251-256, 259-270, 284, 287-288, 303, 305, 309-320, 347-349, 359-364, 397, 400, 413, 417, 423, 434, 438, 456-471, 475-479, 489-490, 494, 505, 525-529, 550, 569-574, 579, 598-602, 620-624, 649-682 |
| cx\_Freeze/exception.py               |        8 |        0 |    100.00% |           |
| cx\_Freeze/executable.py              |      151 |       13 |     91.39% |81, 91-92, 143-144, 227-231, 233, 242-243, 258-260 |
| cx\_Freeze/finder.py                  |      472 |       47 |     90.04% |136, 138, 159, 228-230, 298, 359-362, 402, 404, 447-450, 452-457, 461-462, 494-497, 535-549, 568, 574, 580, 744, 770, 777, 785-786 |
| cx\_Freeze/freezer.py                 |      764 |      101 |     86.78% |90, 135, 153, 156-157, 162-164, 187, 195, 262, 279, 300-301, 308-309, 342, 394, 430-435, 437-442, 446-451, 453-458, 517, 526, 542-543, 551-555, 566-571, 711, 718-721, 728-730, 734, 773, 853-855, 866-867, 871-882, 908-913, 918-923, 954-967, 975-976, 1024, 1065-1068, 1080, 1116-1123, 1135, 1231, 1384, 1388 |
| cx\_Freeze/icons/\_\_init\_\_.py      |        0 |        0 |    100.00% |           |
| cx\_Freeze/module.py                  |      327 |       74 |     77.37% |49, 52-58, 60, 80-99, 108-118, 136, 228, 232, 240-244, 252, 255, 268, 278, 283-284, 300-301, 365, 389-393, 404, 421-422, 426-428, 448-461, 473, 475-478 |
| cx\_Freeze/parser.py                  |      280 |       62 |     77.86% |77, 111, 147, 156, 171, 183-188, 191, 204, 220, 250, 279, 285-289, 296, 303-304, 308-319, 328-333, 337-344, 350, 356-357, 371-373, 377-378, 387, 395, 403-404, 407-409, 414-415 |
| cx\_Freeze/setupwriter.py             |       78 |       78 |      0.00% |     3-123 |
| cx\_Freeze/winmsvcr.py                |        3 |        0 |    100.00% |           |
| cx\_Freeze/winmsvcr\_repack.py        |      158 |       35 |     77.85% |110-111, 113-114, 133, 139-140, 142-143, 214-215, 219-220, 226, 234, 239-242, 250-251, 262-266, 270-299, 309 |
| cx\_Freeze/winversioninfo.py          |      212 |       42 |     80.19% |56, 61-62, 66-74, 142-143, 217, 219, 222-230, 237-239, 259-260, 262-263, 265-266, 359-378 |
|                             **TOTAL** | **4586** |  **895** | **80.48%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/Mu-L/cx_Freeze/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Mu-L/cx_Freeze/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Mu-L/cx_Freeze/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/Mu-L/cx_Freeze/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FMu-L%2Fcx_Freeze%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/Mu-L/cx_Freeze/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.