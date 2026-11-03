# -*- coding: utf-8 -*-
"""从任意目录运行：py -3 08_作品/_共享工具/cookline/run.py <命令>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cookline.cli import main  # noqa: E402

raise SystemExit(main())
