from flask import render_template,request,Blueprint

core = Blueprint('core',__name__)


@core.route('/info')
def info():
    '''
    Example view of any other "core" page. Such as a info page, about page,
    contact page. Any page that doesn't really sync with one of the models.
    '''
    return render_template('info.html')

@core.route('/contact')
def contact():

    return render_template('contact.html')

@core.route('/about')
def about():

    return render_template('about.html')