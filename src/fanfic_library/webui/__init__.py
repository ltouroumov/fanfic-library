from flask import Flask, render_template, request, redirect, url_for

from fanfic_library.cache import thread
from fanfic_library.data import session, Fanfic, Threadmark
from fanfic_library.adapter import create_adapter
from fanfic_library.operations import create_from_thread_url, update_metadata, fetch_chapters

app = Flask(__name__)


def sort_url(sort):
    args = request.view_args.copy()
    args.update(request.args)
    args['s'] = sort
    return url_for(request.endpoint, **args)


app.jinja_env.globals['sort_url'] = sort_url


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        thread_url = request.form['thread_url']

        create_from_thread_url(thread_url)
        return redirect(url_for('index'))

    search = request.args.get('q', None)
    sort = request.args.get('s', 'title')

    fanfics = session.query(Fanfic)

    if search:
        fanfics = fanfics.filter(Fanfic.title.contains(search) | Fanfic.author.contains(search))

    if sort == 'title':
        fanfics = fanfics.order_by(Fanfic.title)
    elif sort == 'author':
        fanfics = fanfics.order_by(Fanfic.author)
    elif sort == 'word-count':
        fanfics = fanfics.order_by(Fanfic.words.desc())
    elif sort == 'id':
        fanfics = fanfics.order_by(Fanfic.id)

    return render_template('index.html', fanfics=fanfics)


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
        threadmarks = session.query(Threadmark).filter(Threadmark.fanfic_id == fanfic.id).order_by(Threadmark.post_id)
        status = {tm.post_id: thread.has_post(fanfic.thread_key, tm.post_id) for tm in threadmarks}

        return render_template('show.html',
                               fanfic=fanfic,
                               threadmarks=threadmarks,
                               status=status,
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
    contents = adapter.get_content(fanfic.thread_key, threadmark.post_id)

    return render_template('view.html',
                           fanfic=fanfic,
                           threadmark=threadmark,
                           contents=contents,
                           prev=prev_tm, next=next_tm,
                           breadcrumbs=[('Index', url_for('index')), (fanfic.title, url_for('show', fid=fanfic.id))])


@app.route('/fic/<int:fid>/refresh', methods=['GET'])
def refresh(fid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()

    update_metadata(fanfic)

    return redirect(url_for('show', fid=fid))


@app.route('/fic/<int:fid>/fetch', methods=['GET'])
def fetch(fid: int):
    fanfic = session.query(Fanfic).filter(Fanfic.id == fid).first()

    fetch_chapters(fanfic)

    return redirect(url_for('show', fid=fid))
