import re
from itertools import groupby
from operator import attrgetter
import pandas as pd
from flask import flash, redirect, url_for, request, make_response, current_app, render_template, escape
from werkzeug.utils import secure_filename, send_from_directory
from sqlalchemy import or_, and_
from flask_login import login_required, current_user

import os
from app import db
from app.blueprints.main import bp
from app.models import Upload

from app.util.helpers import allowed_file, redirect_url


def paginate(items, per_page):
    page = request.args.get('page', 1, type=int)
    items = items.paginate(page=page, per_page=per_page, error_out=False)

    kwargs = request.values.copy()
    if "page" in kwargs:
        del kwargs["page"]

    next_url = url_for(request.endpoint, **kwargs, page=items.next_num) if items.has_next else None
    prev_url = url_for(request.endpoint, **kwargs, page=items.prev_num) if items.has_prev else None
    return items, next_url, prev_url


@bp.route('/', methods=["GET"])
@login_required
def index():
    uploads = Upload.query_by_current_user()
    uploads, next_url, prev_url = paginate(uploads, per_page=50)

    return render_template('main/index.jinja', uploads=uploads.items, pages=uploads.pages, num_uploads=uploads.total,
                           next_url=next_url, prev_url=prev_url)


from parse import Stockholm

# class Sto:
#     def __init__(self, data):
#         self.data = data
#         self.comments = []
#         self.lines = []
#         self.SS_cons = None
#         self._parse()

#     def _parse(self):
#         # Separate data from comments
#         for m in re.finditer(r'^(.+?)/(\d+)-(\d+)\s+([AUGC-]+)$', self.data, re.MULTILINE):
#             self.lines.append({
#                 'name': m.group(1),
#                 'start': int(m.group(2)),
#                 'end': int(m.group(3)),
#                 'seq': m.group(4)
#             })

#         for m in re.finditer(r'^#.+$', self.data, re.MULTILINE):
#             self.comments.append(m.group(0))
#             if m := re.match(r'^#=GC SS_cons +(.+)$', m.group(0)):
#                 self.SS_cons = m.group(1)

#     @property
#     def display(self):
#         table = []
#         for line in self.lines:
#             row = [f"{line['name']}/{line['start']}-{line['end']}", ""]
#             for i, ch in enumerate(line['seq']):
#                 color = 'green' if self.SS_cons[i] == '<' or self.SS_cons[i] == '>' else 'black'
#                 row[1] += f"<span style=\"color: {color}\">{ch}</span>"
#             table.append(row)
#         table.append(["SS_cons", escape(self.SS_cons)])

#         l = max(len(row[0]) for row in table)
#         out = ""
#         for row in table:
#             out += f"{row[0].ljust(l)} {row[1]}\n"
#         out += "\n"

#         for line in self.comments:
#             out += f"{line}\n"
#         return out

@bp.route('/view/<id_>', methods=["GET"])
@login_required
def view(id_):
    upload = Upload.query.filter(Upload.user_id == current_user.id, Upload.id == id_).first_or_404()
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], upload.filename)
    sto = Stockholm.from_file(path)
    return render_template('main/view.jinja', upload=upload, sto=sto)

