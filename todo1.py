import sqlite3,uuid
from flask import Flask,render_template,g, request,url_for,session,flash,redirect,abort

DATABASE='test.db'
USERNAME='admin'
PASSWORD='admin'
SECRET_KEY='This is secret!'

app=Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def welcome():
    return '<h1>Welcome to CMPUT 410 - Jinja Lab!</h1>'

@app.route('/task',methods=['POST','GET'])
def task():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        category=request.form['category']
        priority=request.form['priority']
        description=request.form['description']
        addTask(category,priority,description)
        flash('New task was successfully added')
        return redirect(url_for('task'))
    
    return render_template('show_entries.html',tasks=query_db('select * from tasks'))
def addTask(category,priority,description):
    query_db('insert into tasks(category,priority,description,id) values (?,?,?,?)',[category,int(priority),description,str(uuid.uuid4())], one=True)
    get_db().commit()
    
@app.route('/login',methods=['POST','GET'])
def login():
    error= None
    if request.method=='POST':
        if request.form['username'] != app.config['USERNAME']:
            error='Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error='Invalid Password'
        else:
            session['logged_in']=True
            flash("You are logged in...")
            return redirect(url_for('task'))
    return render_template('login.html',error=error)

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('logged_in',None)
    flash('You are logged out.')
    return redirect(url_for('task'))

@app.route('/delete',methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    #removetask(request.form['category'],request.form['priority'],request.form['description'])
    removetask(request.form['id'])
    flash('Task deleted successfully')
    return redirect(url_for('task'))
#def removetask(category,priority,description):
def removetask(Id):
    #query_db('delete from tasks where category=? and priority=? and description=?',[category,int(priority),description],one=True)
    query_db('delete from tasks where id=?',[Id],one=True)
    get_db().commit()
        
def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db= g._database=sqlite3.connect(DATABASE)
        db.row_factory=sqlite3.Row
    return db
def close_connection():
    db=getattr(g, "_database",None)
    if db is not None:
        db.close
        db=None
def query_db(query,args=(), one=False):
    cursor=get_db().cursor()
    cursor.execute(query,args)
    rv=cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv

if __name__ =='__main__':
    app.debug=True
    app.run()