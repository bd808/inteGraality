#!/usr/bin/python
# -*- coding: utf-8  -*-

import os

from flask import Flask, render_template, request

from pages_processor import PagesProcessor, ProcessingException

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update')
def update():
    page_url = request.args.get('url')
    page_title = request.args.get('page')
    processor = PagesProcessor(page_url)
    try:
        processor.process_one_page(page_title)
        return render_template('update.html', page_title=page_title, page_url=page_url)
    except ProcessingException as e:
        return render_template('update_error.html',
                               page_title=page_title, page_url=page_url, error_message=e)
    except Exception as e:
        return render_template('update_unknown_error.html',
                               page_title=page_title, page_url=page_url, error_type=type(e), error_message=e)


@app.route('/queries')
def queries():
    page_url = request.args.get('url')
    page_title = request.args.get('page')
    property = request.args.get('property')
    processor = PagesProcessor(page_url)
    try:
        stats = processor.make_stats_object_for_page_title(page_title)
        try:
            grouping = stats.GROUP_MAPPING(request.args.get('grouping'))
        except ValueError:
            grouping = request.args.get('grouping')
        positive_query = stats.get_query_for_items_for_property_positive(property, grouping)
        negative_query = stats.get_query_for_items_for_property_negative(property, grouping)
        return render_template('queries.html', page_title=page_title, page_url=page_url,
                               property=property, grouping=request.args.get('grouping'),
                               positive_query=positive_query, negative_query=negative_query)
    except ProcessingException as e:
        return render_template('queries_error.html',
                               page_title=page_title, page_url=page_url, error_message=e)
    except Exception as e:
        return render_template('queries_unknown_error.html',
                               page_title=page_title, page_url=page_url, error_type=type(e), error_message=e)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', title=u'Page not found'), 404


if __name__ == '__main__':
    if os.uname()[1].startswith('tools-webgrid'):
        from flup.server.fcgi_fork import WSGIServer
        WSGIServer(app).run()
    else:
        if os.environ.get('LOCAL_ENVIRONMENT', False):
            app.run(host='0.0.0.0')
        else:
            app.run()
