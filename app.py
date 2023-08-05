from flask import Flask,render_template,request,redirect,url_for,session,flash
from models import *
from controllers import *
from admin import app as admin_app




#==============================Configurations==============================#
app = Flask(__name__)
#app.register_blueprint(admin_app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usercreds.sqlite3'
db.init_app(app)
app.secret_key='secret'
app.app_context().push()
db.create_all()


#==============================Controllers======================================#
@app.route("/")
def start():
    return redirect("/dashboard")


#==============================User======================================#
@app.route('/user/products')
def products():
    products=Products.query.all()
    catalog=Categories.query.all()
    if 'user' in session:
        user=Users.query.filter_by(username=session['user']).first()
        return render_template('products.html',products=products,logged_in=True,user=user,catalog=catalog)
    else:
        return render_template('products.html',products=products,logged_in=False,user="Guest")
@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=Users(username=username,password=password)
        userlist=[value[0] for value in Users.query.with_entities(Users.username).all()]
        if user.username not in userlist:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('sign_up.html',message=0)
    return render_template('sign_up.html',message=1)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=Users.query.filter_by(username=username,password=password).first()
        if user:
            session['user']=user.username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',message=0)
    return render_template('login.html',message=1)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if request.method=='POST':
        category=request.form.get('category')
        if not category:
            return "Failed to load categories"
        return redirect(f"/user/filter/{category}")
    category=Categories.query.all()
    if not category:
        return "Failed to load categories"
    products=Products.query.all()[:5]
    if "user" not in session:
        return render_template('dashboard2.html',products=products,logged_in=False,user="Guest",message=2,categories=category)
    
    user=Users.query.filter_by(username=session['user']).first()
    return render_template('dashboard2.html',products=products,logged_in=True,user=user,message=2,catalog=category)


@app.route('/user/view_product/<int:id>',methods=['GET','POST'])
def view_product(id):
    pro=Products.query.filter_by(product_id=id).first()
    products=Products.query.all()
    if request.method=='GET':
        return render_template('view_product.html',product=pro)
    else:
        quantity=request.form.get('quantity')
        item=User_cart(username=session['user'],product_id=id,product_name=pro.product_name,quantity=quantity,unit_cost=pro.product_price,cost=int(quantity)*int(pro.product_price),image_url=pro.image_url,category=pro.category)
        db.session.add(item)
        db.session.commit()
        return render_template('dashboard2.html',logged_in=True,products=products,message=1,user=session['user'])

@app.route('/user/filter/<string:cat_name>',methods=['GET','POST'])
def filter(cat_name):
    products=Products.query.filter_by(category=cat_name).all()
    if cat_name=='all':
        products=Products.query.all()
    if "user" in session:
        return render_template('products.html',logged_in=True,products=products,user=session['user'],catalog=Categories.query.all())
    
    return render_template('products.html',logged_in=False,products=products,catalog=Categories.query.all(),user="Guest")

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user',None)
        return redirect(url_for('login'))
    

    

        










#==============================Admin======================================#
@app.route('/admin/register',methods=['GET','POST'])
def admin_register():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        admin=Admins(username=username,password=password)
        db.session.add(admin)
        db.session.commit()
        return redirect("/admin/login")
        
    else:
        return render_template('admin_register.html')


@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        admin=Admins.query.filter_by(username=username,password=password).first()
        if admin:
            session["admin"]=username
            return redirect("/admin/home")
        else:
            return render_template('admin_login.html',message=0)
    return render_template('admin_login.html',message=1)
        
# @app.route('/home',methods=['GET','POST'])
# def home():
#     return render_template('home.html')

@app.route('/admin/home',methods=['GET','POST'])
def admin_home():
    products=Products.query.all()
    if "admin" in session:
        return render_template('admin_home.html',products=products)
    return redirect("/admin/login")

@app.route('/admin/add_product',methods=['GET','POST'])
def add_product():
    catlist=Categories.query.all()
    if request.method=='GET':
        return render_template('add_product.html',message=0,catlist=catlist)
    if request.method=='POST':
        product_name=request.form.get('name')
        product_price=request.form.get('price')
        inventory_count=request.form.get('quantity')
        cat_name=request.form['cat_name']
        image=request.form.get('image_url')
        image="/static/"+image
        if not cat_name:
            return "fail"
        product=Products(product_name=product_name,product_price=product_price,inventory_count=inventory_count,image_url=image,category=cat_name)
        db.session.add(product)
        db.session.commit()
        return render_template('admin_home.html',message=1,products=Products.query.all())


@app.route('/admin/delete_product/<int:id>',methods=['GET','POST'])
def delete_product(id):
    pro=Products.query.filter_by(product_id=id).first()
    db.session.delete(pro)
    db.session.commit()
    return redirect(url_for('admin_home'))


@app.route('/admin/edit_product/<int:id>',methods=['GET','POST'])
def edit_product(id):
    pro=Products.query.filter_by(product_id=id).first()
    products=Products.query.all()
    if request.method=='GET':
        return render_template('edit_product.html',product=pro)
    else:
        pro.product_name=request.form.get('name')
        pro.product_price=request.form.get('price')
        pro.inventory_count=request.form.get('quantity')
        db.session.commit()
        return render_template('admin_home.html',products=products,message=2)



@app.route('/admin/refill/<int:id>',methods=['GET','POST'])
def refill(id):
    product=Products.query.filter_by(product_id=id).first()
    if request.method=='GET':
        return render_template('refill.html',product=product)
    else:
        addn=request.form.get('quantity')
        product.inventory_count+=int(addn)
        #db.session.commit()
        return render_template('admin_home.html',products=Products.query.all(),message=2) 
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin',None)
    flash("You have been logged out","info")
    return redirect(url_for('admin_login'))       

@app.route('/admin/add_category',methods=['GET','POST'])
def add_category():
    if request.method=='GET':
        return render_template('add_cat.html',message=0)
    else:
        cat_name=request.form.get('cat_name')
        cat=Categories(cat_name=cat_name)
        db.session.add(cat)
        db.session.commit()
        return render_template('add_cat.html',message=1)
        
















#==============================User Cart======================================#
#==============================Cart======================================#


@app.route('/user/cart',methods=['GET','POST'])
def cart():
    
    user=Users.query.filter_by(username=session["user"]).first()
    items=User_cart.query.filter_by(username=session["user"]).all()
    
    return render_template('cart.html',items=items,user=user,logged_in=True)

@app.route('/user/cart/test',methods=['GET','POST'])
def test():
    user=Users.query.filter_by(username=session['user']).first()
    cart=User_cart.query.filter_by(username=user.username).all()
    print(cart)
    for item in cart:
        id=item.product_id
        count=item.quantity
        pro=Products.query.filter_by(product_id=item.product_id).first()
        print(pro)
        
        if not pro:
            return str(id)
        pro.inventory_count-=count
        db.session.delete(item)
    db.session.commit()
    return "checked out successfully"

    


    



@app.route('/user/cart/update/<int:id>',methods=['GET','POST'])
def update_item(id):
    item=User_cart.query.filter_by(entry_id=id).first()
    if item:
        if request.method=='GET':
            return render_template('update_item.html',item=item,message=1)
        if request.method=='POST':
            req_qty=request.form.get('quantity')
            product_id=item.product_id
            product=Products.query.filter_by(product_id=product_id).first()
            if item.quantity<product.inventory_count:
                item.quantity=req_qty
                item.cost=int(item.quantity)*int(item.unit_cost)
                db.session.commit()
                return redirect("/user/cart")
            else:
                #flash("Not enough inventory","info")
                return render_template('update_item.html',item=item,message=0)
    else:
        return str(id)+"failed"
        

#==============================Main======================================#
if __name__=='__main__':
    app.run(debug=True)
    

    