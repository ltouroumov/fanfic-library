import itertools
from pprint import pprint

from flask import Flask, render_template, request, redirect, url_for

from fanfic_library import utils
from fanfic_library.data import session, Fanfic, Threadmark
from fanfic_library.adapter import create_adapter
app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        thread_url = request.form['thread_url']

        adapter = create_adapter(thread_url)
        fanfic = adapter.fetch_metadata()
        session.add(fanfic)
        session.commit()
        return redirect(url_for('index'))

    return render_template('index.html', fanfics=session.query(Fanfic))


@app.route('/fic/<int:fid>', methods=['GET'])
def show(fid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()

    action = request.args.get('do', 'show')
    if action == 'delete':
        session.delete(fanfic)
        session.commit()
        return redirect(url_for('index'))
    elif action == 'edit':
        return 'Not Implemented'
    else:
        return render_template('show.html',
                               fanfic=fanfic,
                               threadmarks=session.query(Threadmark).filter(Threadmark.fanfic_id == fanfic.id).order_by(Threadmark.post_id),
                               breadcrumbs=[('Index', url_for('index'))])


@app.route('/fic/<int:fid>/edit', methods=['GET', 'POST'])
def edit(fid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()

    if request.method == 'POST':
        fanfic.title = request.form['title']
        fanfic.author = request.form['author']
        fanfic.words = request.form['words']
        fanfic.summary = request.form['summary']
        session.commit()
        return redirect(url_for('show', fid=fanfic.id))
    else:
        return render_template('edit.html',
                               fanfic=fanfic,
                               breadcrumbs=[('Index', url_for('index'))])


@app.route('/fic/<int:fid>/post/<int:tmid>', methods=['GET'])
def view(fid: int, tmid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()
    threadmark = session.query(Threadmark).filter(Threadmark.post_id == tmid).first()

    prev_tm = session.query(Threadmark)\
        .filter(Threadmark.fanfic_id == fanfic.id, Threadmark.post_id < tmid)\
        .order_by(Threadmark.post_id.desc())\
        .first()

    next_tm = session.query(Threadmark) \
        .filter(Threadmark.fanfic_id == fanfic.id, Threadmark.post_id > tmid) \
        .order_by(Threadmark.post_id.asc()) \
        .first()

    adapter = create_adapter(fanfic.thread_url)
    contents = adapter.get_content(fanfic.id, threadmark.post_id)

    return render_template('view.html',
                           fanfic=fanfic,
                           threadmark=threadmark,
                           contents=contents,
                           prev=prev_tm, next=next_tm,
                           breadcrumbs=[('Index', url_for('index')), (fanfic.title, url_for('show', fid=fanfic.id))])


@app.route('/fic/<int:fid>/refresh', methods=['GET'])
def refresh(fid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()
    adapter = create_adapter(fanfic.thread_url)

    update_fanfic(adapter, fanfic)

    word_count = update_threadmarks(adapter, fanfic)

    fanfic.words = word_count
    session.commit()

    return redirect(url_for('show', fid=fid))


def update_fanfic(adapter, fanfic):
    cur_fanfic = adapter.fetch_metadata()
    fanfic.update_with(cur_fanfic)


def update_threadmarks(adapter, fanfic):
    old_threadmarks = utils.make_ordered_dict(fanfic.threadmarks, key=lambda tm: tm.post_id)
    cur_threadmarks = adapter.fetch_threadmarks(fanfic.id)
    new_threadmarks = []
    pprint(old_threadmarks)
    for cur_tm in cur_threadmarks:
        old_tm = old_threadmarks.get(cur_tm.post_id, None)
        if old_tm is None:
            new_threadmarks.append(cur_tm)
        elif hash(cur_tm) != hash(old_tm):
            old_tm.update_with(cur_tm)
    session.add_all(new_threadmarks)

    return sum(tm.words for tm in itertools.chain(old_threadmarks.values(), new_threadmarks))
