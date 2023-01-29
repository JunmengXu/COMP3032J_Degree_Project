import pickle
import re
import requests
import xgboost
import pandas
from flask import render_template, redirect, session, url_for, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from . import main
from .forms import LoginForm, RegisterForm, CalculationForm, FilterForm, SearchForm,AgentLoginForm,RecommendationForm
from .. import db
from ..models import User,Property, Agent,Community,FavoriteProperty
from sqlalchemy import or_, and_, func
from fuzzywuzzy import process

evaluation_model = pickle.load(open("models/evaluation_model.pkl", "rb"))
business_pca = pickle.load(open("models/business_pca.pkl", "rb"))
business_locations = pickle.load(open("models/business_locations.pkl", "rb"))
with open("category-number.txt", "rb") as f:
	categoryNumber = pickle.load(f)
districtPair = [(v, k)for k, v in categoryNumber["district"].items()]
townPair = [(v, k)for k, v in categoryNumber["town"].items()]
town_dic = dict(townPair)
district_dic = dict(districtPair)
district_dic[-1] = None
with open("district_town.txt", "rb") as f:
    district_town = pickle.load(f)
districts = [k for k, v in categoryNumber["district"].items()]
towns = [k for k, v in categoryNumber["town"].items()]

with open("community_id.txt", "rb") as f:
    community_id = pickle.load(f)
communities = [k for k, v in community_id.items()]

with open("town-business.txt","rb") as f:
    town_business = pickle.load(f)

@main.route('/', methods=['POST', 'GET'])
@main.route('/index', methods=['POST', 'GET'])
def index():
    form = SearchForm()
    register_form = RegisterForm()
    login_form = LoginForm()
    if form.is_submitted():
        query = form.query.data
        query = 'hs'+query
        return redirect(url_for('main.properties_search', query=query,_external=True))

    if not session.get("USERNAME") is None:
        user = User.query.filter(
            User.username == session.get("USERNAME")).first()
        return render_template('main/home.html', form=form, register_form=register_form, login_form=login_form, template='main/template_after_login.html', user=user)
    else:
        return render_template('main/home.html', form=form, register_form=register_form, login_form=login_form, template='main/template.html')


@main.route('/handle_register', methods=['POST'])
def register():
    form = RegisterForm(request.form)
    print('get register')
    if form.validate_on_submit():       
        passw_hash = generate_password_hash(form.register_password.data)
        user = User(username=form.register_username.data,email=form.email.data, password_hash=passw_hash)
        db.session.add(user)
        db.session.commit()
        session["USERNAME"] = user.username
        print('register succesful')
    return redirect(request.referrer)

@main.route('/checkemail', methods=['POST'])
def check_email():
    email = request.form['email']
    email_in_db = User.query.filter(User.email == email).first()
    if not email_in_db:
        return jsonify({'status': 0})
    else:
        return jsonify({'status': 1})

@main.route('/checkusername', methods=['POST'])
def check_username():
    print('get_post')
    username = request.form['username']
    user_in_db = User.query.filter(User.username == username).first()
    if not user_in_db:
        return jsonify({'status': 0})
    else:
        print('has such user')
        return jsonify({'status': 1})

@main.route('/handle_login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        agent_email_re = r'^[\w\.-]+@liveulike\.com$'
        agent_match = re.match(agent_email_re, form.login_email.data)
        if agent_match:
            agent_in_db = Agent.query.filter(Agent.email == form.login_email.data).first()
            if not agent_in_db:
               return jsonify({'error':'No such user, please check your login information again!'})
            if (check_password_hash(agent_in_db.password_hash, form.login_password.data)):
                print('correct password')
                session["AGENT"] = agent_in_db.username
                return jsonify({'error':'none','user':'agent'})
            return jsonify({'error':'Password or Username is not correct!'})
        else:
            user_in_db = User.query.filter(User.email == form.login_email.data).first()
            if not user_in_db:
                return jsonify({'error':'No such user, please check your login information again!'})
            if (check_password_hash(user_in_db.password_hash, form.login_password.data)):
                session["USERNAME"] = user_in_db.username
                return jsonify({'error':'none','user':'customer'})
            return jsonify({'error':'Password or Username is not correct!'})
    return redirect(request.referrer)


@main.route('/handle_logout', methods=['GET'])
def logout():
    session.pop("USERNAME", None)
    return redirect(request.referrer)


@main.route('/properties', methods=['GET', 'POST'])
def properties():
    register_form = RegisterForm()
    login_form = LoginForm()

    form = FilterForm()
    page = int(request.args.get('page', 1))
    properties = Property.query.filter(Property.status==1).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)

    if request.method == 'POST':
        print('redirect')
        form = FilterForm(request.form)
        return redirect(url_for('main.properties_filter', query=dic_to_str(form.data),_external=True))

    if not session.get("USERNAME") is None:
        user = User.query.filter(User.username == session.get("USERNAME")).first()
        return render_template('main/properties_all.html', house_paginate=properties, form=form, template='main/template_after_login.html', user=user)
    else:
        return render_template('main/properties_all.html', house_paginate=properties, form=form, template='main/template.html', register_form=register_form, login_form=login_form)

@main.route('/properties/<query>', methods=['GET', 'POST'])
def properties_filter(query):
    register_form = RegisterForm()
    login_form = LoginForm()
    form = FilterForm(data=str_to_dic(query))
    district = district_dic[form.district.data]
    size_range = re.match(r'\((\d+), (\d+)\)', form.size.data)
    price_range = re.match(r'\((\d+), (\d+)\)', form.price.data)
    room_number = form.room.data
    page = int(request.args.get('page', 1))

    filter_condition = ''
    if district == None:
        if size_range != None and price_range != None and room_number != 'None':
            price_below = int(price_range.group(1)) * 10000
            price_above = int(price_range.group(2)) * 10000
            filter_condition = and_(Property.square >= size_range.group(1), Property.square <= size_range.group(2), (Property.square * Property.price) >=
                                    price_below, (Property.square * Property.price) <= price_above, (Property.bathroom+Property.bedroom+Property.kitchen) == int(room_number))
        else:
            if size_range == None:
                if price_range == None and room_number != 'None':
                    filter_condition = and_(
                        (Property.bathroom+Property.bedroom+Property.kitchen) == int(room_number))
                elif price_range != None and room_number == 'None':
                    price_below = int(price_range.group(1)) * 10000
                    price_above = int(price_range.group(2)) * 10000
                    filter_condition = and_((Property.square * Property.price) >=
                                            price_below, (Property.square * Property.price) <= price_above)
                else:
                    filter_condition = not None
            else:
                if price_range == None and room_number != 'None':
                    filter_condition = and_((Property.bathroom+Property.bedroom+Property.kitchen) == int(
                        room_number), Property.square >= size_range.group(1), Property.square <= size_range.group(2))
                elif price_range != None and room_number == 'None':
                    price_below = int(price_range.group(1)) * 10000
                    price_above = int(price_range.group(2)) * 10000
                    filter_condition = and_((Property.square * Property.price) >= price_below, (Property.square * Property.price)
                                            <= price_above, Property.square >= size_range.group(1), Property.square <= size_range.group(2))
                else:
                    filter_condition = and_(Property.square >= size_range.group(
                        1), Property.square <= size_range.group(2))
    else:
        if size_range != None and price_range != None and room_number != 'None':
            price_below = int(price_range.group(1)) * 10000
            price_above = int(price_range.group(2)) * 10000
            filter_condition = and_(Property.district == district, Property.square >= size_range.group(1), Property.square <= size_range.group(
                2), (Property.square * Property.price) >= price_below, (Property.square * Property.price) <= price_above, (Property.bathroom+Property.bedroom+Property.kitchen) == int(room_number))
        else:
            if size_range == None:
                if price_range == None and room_number != 'None':
                    filter_condition = and_(Property.district == district, (
                        Property.bathroom+Property.bedroom+Property.kitchen) == int(room_number))
                elif price_range != None and room_number == 'None':
                    price_below = int(price_range.group(1)) * 10000
                    price_above = int(price_range.group(2)) * 10000
                    filter_condition = and_(Property.district == district, (Property.square * Property.price)
                                            >= price_below, (Property.square * Property.price) <= price_above)
                else:
                    filter_condition = Property.district == district
            else:
                if price_range == None and room_number != 'None':
                    filter_condition = and_(Property.district == district, (Property.bathroom+Property.bedroom+Property.kitchen) == int(
                        room_number), Property.square >= size_range.group(1), Property.square <= size_range.group(2))
                elif price_range != None and room_number == 'None':
                    price_below = int(price_range.group(1)) * 10000
                    price_above = int(price_range.group(2)) * 10000
                    filter_condition = and_(Property.district == district, (Property.square * Property.price) >= price_below, (Property.square *
                                            Property.price) <= price_above, Property.square >= size_range.group(1), Property.square <= size_range.group(2))
                else:
                    filter_condition = and_(Property.district == district, Property.square >= size_range.group(
                        1), Property.square <= size_range.group(2))

    properties = Property.query.filter(and_(filter_condition,Property.status==1)).paginate(
        page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
    properties_quantity = len(properties.items)

    if properties_quantity == 0:

        if not session.get("USERNAME") is None:
            user = User.query.filter(
                User.username == session.get("USERNAME")).first()
            return render_template('main/properties_filter.html', house_paginate=properties, filter=query, form=form, no_result=True, template='main/template_after_login.html', user=user,title='Properties',type_='filter')
        else:
            return render_template('main/properties_filter.html', house_paginate=properties, filter=query, form=form, no_result=True, template='main/template.html', register_form=register_form, login_form=login_form,title='Properties',type_='filter')

    else:
        if not session.get("USERNAME") is None:
            user = User.query.filter(
                User.username == session.get("USERNAME")).first()
            return render_template('main/properties_filter.html', house_paginate=properties, filter=query, form=form, no_result=False, template='main/template_after_login.html', user=user,title='Properties',type_='filter')
        else:
            return render_template('main/properties_filter.html', house_paginate=properties, filter=query, form=form, no_result=False, template='main/template.html', register_form=register_form, login_form=login_form,title = 'Properties',type_='filter')


@main.route('/properties/search/<query>', methods=['GET', 'POST'])
def properties_search(query):
    register_form = RegisterForm()
    login_form = LoginForm()
    form = FilterForm()
    page = int(request.args.get('page', 1))
    keywords = re.match(r'hs(.+)',query)
    
    if not keywords:
        return redirect(url_for('main.properties'))
    else:
        keyword = keywords.group(1)

    filter_condition = and_(or_(Property.district.like(
        '%'+keyword+'%'), Property.town.like('%'+keyword+'%')),Property.status==1)
    properties = Property.query.filter(filter_condition).paginate(
        page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)

    count = len(properties.items)
    if count == 0:
        no_result = True
    else:
        no_result = False
    
    if form.is_submitted():
        return redirect(url_for('main.properties_filter', query=dic_to_str(form.data),_external=True))

    if not session.get("USERNAME") is None:
        user = User.query.filter(
            User.username == session.get("USERNAME")).first()
        return render_template('main/properties_filter.html', house_paginate=properties, filter='search/{}'.format(query), form=form, template='main/template_after_login.html', user=user,no_result = no_result,title='Search Results for: {}'.format(keyword),type_='search')
    else:
        return render_template('main/properties_filter.html', house_paginate=properties, filter='search/{}'.format(query), form=form, template='main/template.html', register_form=register_form, login_form=login_form,no_result=no_result,title='Search Results for: {}'.format(keyword),type_='search')


@main.route('/autocomplete', methods=['POST'])
def search_autocomplete():
    keyword = request.form['keyword']
    district_rank = process.extract(keyword, districts, limit=5)
    town_rank = process.extract(keyword, towns, limit=5)
    district_rank_dic = {}
    town_rank_dic = {}
    for i in district_rank:
        district_rank_dic[i] = 'district'
    for i in town_rank:
        town_rank_dic[i] = 'town'
    district_rank_dic.update(town_rank_dic)
    sorted_dic = sorted(district_rank_dic.items(),
                        key=lambda d: d[0][1], reverse=True)
    return jsonify({'rank': sorted_dic[:5]})


def dic_to_str(dic):
    string = ''
    for k in dic.keys():
        if k == 'csrf_token':
            pass
        else:
            string += '{}={}&'.format(k, dic[k])
    return string


def str_to_dic(query):
    dic = {}
    pairs = query.split('&')
    for pair in pairs[:-1]:
        key_value = pair.split('=')
        key = key_value[0]
        value = key_value[1]
        if value == 'True':
            value = True
        elif value == 'False':
            value = False

        dic[key] = value

    return dic


@main.route("/house/<int:id>",methods=['GET','POST'])
def house(id):
    # Forms
    register_form = RegisterForm()
    login_form = LoginForm()
    recommendation_form = RecommendationForm()
    # Current house
    house = Property.query.filter_by(id=id).first()
    if house:
        agent = Agent.query.filter(Agent.id == house.agent_id).first()
        total = int((house.price * house.square)/1000)
        district = house.district
        filter_condition_noresult = and_(Property.district == district)
        room_number = house.bedroom + house.bathroom + house.kitchen
        page = int(request.args.get('page', 1))

        size_range = [house.square - 50, house.square + 50]
        price_range = [(house.price - 15000) * house.square, (house.price + 15000) * house.square]
        room_range = [room_number - 2, room_number + 2]

        string = ''

        if not recommendation_form.is_submitted():
            filter_condition = and_(Property.district==district, Property.square>size_range[0],Property.square<size_range[1],
                                    (Property.square * Property.price)>price_range[0],(Property.square * Property.price)<price_range[1],
                                    (Property.bathroom+Property.bedroom+Property.kitchen) > room_range[0], (Property.bathroom+Property.bedroom+Property.kitchen)<room_range[1],
                                    and_(Property.square!=house.square, Property.price!=house.price))
            string = 'similar properties with the current one'
            properties = Property.query.filter(filter_condition).paginate(page,current_app.config["SQLALCHEMY_NUM_PER_PAGE"],False)

        #
        # 数据可视化
        #
        house_chart = Property.query.filter(Property.status != 0).all()

        # 得到所有房子的district和price信息
        district_price_list = []
        for houseitem in house_chart:
            district_price_list.append([houseitem.district, houseitem.price])

        # 转换数据格式为dataframe
        house_chartp = pandas.DataFrame(district_price_list, columns=["district", "price"])

        # 对district分组
        grouped = house_chartp.groupby('district')
        # 用quantile计算分位数

        chart = []
        quan = 0.1
        thirdIndex = 0
        while (quan <= 1):
            price_quantile = grouped['price'].quantile(quan)
            price_quantile_list = price_quantile.tolist()
            district_quantile_list = price_quantile.index.tolist()
            for i in range(len(price_quantile_list)):
                if district_quantile_list[i] == 'Changping':
                    chart.append([0, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Chaoyang':
                    chart.append([1, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Daxing':
                    chart.append([2, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Dongcheng':
                    chart.append([3, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Fangshan':
                    chart.append([4, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Fengtai':
                    chart.append([5, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Haidian':
                    chart.append([6, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Mentougou':
                    chart.append([7, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Shijingshan':
                    chart.append([8, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Shunyi':
                    chart.append([9, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Tongzhou':
                    chart.append([10, thirdIndex, price_quantile_list[i] / 1000])
                elif district_quantile_list[i] == 'Xicheng':
                    chart.append([11, thirdIndex, price_quantile_list[i] / 1000])
            quan = quan + 0.1
            thirdIndex = thirdIndex + 1

        currentX = 0
        currentY = 0
        house_district_index = 0
        if house.district == 'Changping':
            house_district_index = 0
        elif house.district == 'Chaoyang':
            house_district_index = 1
        elif house.district == 'Daxing':
            house_district_index = 2
        elif house.district == 'Dongcheng':
            house_district_index = 3
        elif house.district == 'Fangshan':
            house_district_index = 4
        elif house.district == 'Fengtai':
            house_district_index = 5
        elif house.district == 'Haidian':
            house_district_index = 6
        elif house.district == 'Mentougou':
            house_district_index = 7
        elif house.district == 'Shijingshan':
            house_district_index = 8
        elif house.district == 'Shunyi':
            house_district_index = 9
        elif house.district == 'Tongzhou':
            house_district_index = 10
        elif house.district == 'Xicheng':
            house_district_index = 11

        currentY = house_district_index
        for item in chart:
            if item[0] == house_district_index:
                if item[2] <= house.price / 1000:
                    currentX = item[1]


        if not session.get("USERNAME") is None:
            user = User.query.filter(User.username == session.get("USERNAME")).first()
            favorite = FavoriteProperty.query.filter(and_(FavoriteProperty.property_id==id,FavoriteProperty.user_id==user.id)).first()
            return render_template("main/property_single.html",house=house, form=recommendation_form,template='main/template_after_login.html', 
                    user=user, total=total,agent = agent,favorite_status=favorite, house_paginate=properties, string=string, chart=chart, currentX=currentX,currentY=currentY)
        else:
            return render_template("main/property_single.html",template = 'main/template.html',register_form = register_form,login_form = login_form,house=house,total=total,agent =agent,form=recommendation_form, 
                                house_paginate=properties, string=string,user=None, chart=chart, currentX=currentX,currentY=currentY)
    else:
        return redirect(url_for('main.index',_external=True))

@main.route('/handle_recommendation/<id>',methods=['POST'])
def handle_recommendation(id):
    print('get post')
    house = Property.query.filter_by(id=id).first()
    recommendation_form = RecommendationForm(request.form)
    district = house.district
    filter_condition_noresult = and_(Property.district == district)
    filter_condition_recommend = (Property.district == district)
    room_number = house.bedroom + house.bathroom + house.kitchen
    page = int(request.args.get('page', 1))

    size_range = [house.square - 50, house.square + 50]
    price_range = [(house.price - 15000) * house.square, (house.price + 15000) * house.square]
    room_range = [room_number - 2, room_number + 2]

    option = recommendation_form.options.data

    string = ''
    if option == 1:  # 更少价格 按钮被单击
        filter_condition_recommend = and_(Property.district==district, Property.square>size_range[0],Property.square<size_range[1],
                            (Property.square * Property.price)<house.price * house.square,
                            (Property.bathroom+Property.bedroom+Property.kitchen) > room_range[0], (Property.bathroom+Property.bedroom+Property.kitchen)<room_range[1],
                            and_(Property.square!=house.square, Property.price!=house.price))
        string = 'less price'
    elif option==2:  # 更少面积 按钮被单击
        filter_condition_recommend = and_(Property.district == district, Property.square < house.square,
                                        (Property.square * Property.price)>price_range[0],(Property.square * Property.price)<price_range[1],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) > room_range[0],(Property.bathroom + Property.bedroom + Property.kitchen) < room_range[1],
                                        and_(Property.square != house.square, Property.price != house.price))
        string = 'less size'
    elif option == 3:  # 更多面积 按钮被单击
        filter_condition_recommend = and_(Property.district == district, Property.square > house.square,
                                (Property.square * Property.price) > price_range[0],(Property.square * Property.price) < price_range[1],
                                (Property.bathroom + Property.bedroom + Property.kitchen) > room_range[0], (Property.bathroom + Property.bedroom + Property.kitchen) < room_range[1],
                                and_(Property.square != house.square, Property.price != house.price))
        string = 'more price'
    elif option == 4:  # 更少房间 按钮被单击
        filter_condition_recommend = and_(Property.district == district, Property.square > size_range[0],Property.square < size_range[1],
                                        (Property.square * Property.price) > price_range[0],(Property.square * Property.price) < price_range[1],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) < room_number,
                                        and_(Property.square != house.square, Property.price != house.price))
        string = 'less room'
    elif option == 5:  # 更多房间 按钮被单击
        filter_condition_recommend = and_(Property.district == district, Property.square > size_range[0],
                                        Property.square < size_range[1],
                                        (Property.square * Property.price) > price_range[0],
                                        (Property.square * Property.price) < price_range[1],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) > room_number,
                                        and_(Property.square != house.square, Property.price != house.price))
        string = 'more room'
    elif option == 6:  # 更低楼层 按钮被单击
        print('lower floor')
        filter_condition_recommend = and_(Property.district == district, Property.square > size_range[0],
                                        Property.square < size_range[1],
                                        (Property.square * Property.price) > price_range[0],
                                        (Property.square * Property.price) < price_range[1],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) > room_range[0],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) < room_range[1],
                                        Property.floorHeight < house.floorHeight,
                                        and_(Property.square != house.square, Property.price != house.price))
        string = 'lower floor'
    elif option == 7:  # 更高楼层 按钮被单击
        print('more floor')
        filter_condition_recommend = and_(Property.district == district, Property.square > size_range[0],
                                        Property.square < size_range[1],
                                        (Property.square * Property.price) > price_range[0],
                                        (Property.square * Property.price) < price_range[1],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) > room_range[0],
                                        (Property.bathroom + Property.bedroom + Property.kitchen) < room_range[1],
                                        Property.floorHeight > house.floorHeight,
                                        and_(Property.square != house.square, Property.price != house.price))
        string = 'higher floor'
    else: ## default 0
        filter_condition_recommend = and_(Property.district==district, Property.square>size_range[0],Property.square<size_range[1],
                                    (Property.square * Property.price)>price_range[0],(Property.square * Property.price)<price_range[1],
                                    (Property.bathroom+Property.bedroom+Property.kitchen) > room_range[0], (Property.bathroom+Property.bedroom+Property.kitchen)<room_range[1],
                                    and_(Property.square!=house.square, Property.price!=house.price))
        string = None


    properties = Property.query.filter(filter_condition_recommend).paginate(page, current_app.config[
        "SQLALCHEMY_NUM_PER_PAGE"], False)
    count = len(properties.items)
    if count == 0:
        properties = Property.query.filter(filter_condition_noresult).paginate(page,current_app.config["SQLALCHEMY_NUM_PER_PAGE"],False)
        string = 'sorry, no similar/such properties, maybe you like these'

    
    return render_template("main/recommendation_section.html", house_paginate=properties, string=string,house=house,count=count)

@main.route('/test', methods=['GET', 'POST'])
def test():
    print('get post')
    return render_template('main/test.html')

@main.route('/price_calculator', methods=['GET', 'POST'])
def price_calculator():
    register_form = RegisterForm()
    login_form = LoginForm()
    form = CalculationForm()
    form.town.choices = get_towns(0) #default: chaoyang
    form.business.choices=[(value) for value in town_business[0]]
    if request.method == 'GET':
        if not session.get("USERNAME") is None:
            user = User.query.filter(User.username == session.get("USERNAME")).first()
            return render_template('main/price_calculator.html',form=form,template = 'main/template_after_login.html',user=user)
        else:
            return render_template('main/price_calculator.html',form=form,template = 'main/template.html',register_form = register_form,login_form = login_form)

    if request.method == 'POST':
        new_form = CalculationForm(request.form, meta=form)
        d_code = new_form.district.data
        choices = get_towns(d_code)
        # print(dict(choices))
        return jsonify({'choices':dict(choices)})

def get_towns(d_code):
    t_codes = district_town[str(d_code)]
    choices = []
    for pair in townPair:
        code = str(pair[0])
        if code in t_codes:
            choices.append(pair)
    return choices

@main.route('/change_town', methods=['POST'])
def change_town():
    form = CalculationForm(request.form)
    # print(list(town_business[int(form.town.data)]))
    return jsonify({'choices':list(town_business[int(form.town.data)])})

@main.route('/calculation', methods=['POST'])
def calculation():
    form = CalculationForm(request.form)
    register_form = RegisterForm()
    login_form = LoginForm()
    # print(form.data)
    town_name = town_dic[int(form.town.data)]
    locationJson = requests.get(
        'http://api.map.baidu.com/place/v2/search?query={q}&region=%E5%8C%97%E4%BA%AC&output=json&ak=cYP3zeUAoU5ECvESplsoQt8PCEoi8VXR'.format(
            q=town_name)).json()

    if locationJson["status"] != 0:
        return jsonify({'price': "Acquiring location failed."})

    business=form.business.data
    business_locations_copy=business_locations.copy()
    batch=[]
    for location in business.split(","):
        if location in business_locations_copy:
            batch.append(location)
    business_locations_copy[batch]=1
    business_transformed=business_pca.transform([business_locations_copy])

    if form.validate_on_submit():
        print('Validate and Submit')
        price = evaluation_model.predict(xgboost.DMatrix(pandas.DataFrame({
            "Lng": [locationJson["results"][0]["location"]["lng"]],
            "Lat": [locationJson["results"][0]["location"]["lat"]],
            "tradeTime": [2021],
            "square": [form.square.data],
            "livingRoom": [form.livingRoom.data],
            "drawingRoom": [form.drawingRoom.data],
            "kitchen": [form.kitchen.data],
            "bathRoom": [form.bathRoom.data],
            "buildingType": [form.buildingType.data],
            "constructionTime": [form.constructionTime.data],
            "renovationCondition": [form.renovationCondition.data],
            "buildingStructure": [form.buildingStructure.data],
            "elevator": [form.elevator.data],
            "fiveYearsProperty": [form.fiveYearsProperty.data],
            "subway": [form.subway.data],
            "district": [form.district.data],
            "town": [int(form.town.data)],
            "floorType": [form.floorType.data],
            "floorHeight": [form.floorHeight.data],
            "name0":[business_transformed[0][0]],
            "name1": [business_transformed[0][1]],
            "name2": [business_transformed[0][2]],
        })))[0]
        # print(type(evaluation_model.get_fscore()))
        per_price = "{:,}".format(int(price))
        total_price = "{:,}".format(int(price) * int(form.square.data))
        if not session.get("USERNAME") is None:
            user = User.query.filter(User.username == session.get("USERNAME")).first()
            return render_template('main/calculation_result.html', per=per_price, total=total_price,
                                   template='main/template_after_login.html', user=user,
                                   district_average={key: value for key, value in \
                                                     db.session.query(Property.district,
                                                                      func.avg(Property.price)).filter_by(
                                                         tradeTime="2021").group_by(Property.district).all()},
                                   ml_feature_importance=evaluation_model.get_fscore(),
                                   price=price)
        else:
            return render_template('main/calculation_result.html', per=per_price, total=total_price,
                                   template='main/template.html', register_form=register_form, login_form=login_form,
                                   district_average={key: value for key, value in \
                                                     db.session.query(Property.district,
                                                                      func.avg(Property.price)).filter_by(
                                                         tradeTime="2021").group_by(Property.district).all()},
                                   ml_feature_importance=evaluation_model.get_fscore(),
                                   price=price)
    else:
        print(form.errors)
        return jsonify({'price': 'Please enter all fileds'})

@main.route('/calculation_result', methods=['GET','POST'])
def calculation_result():
    register_form = RegisterForm()
    login_form = LoginForm()
    if not session.get("USERNAME") is None:
        user = User.query.filter(User.username == session.get("USERNAME")).first()
        return render_template('main/calculation_result.html',template = 'main/template_after_login.html',user=user)
    else:
        return render_template('main/calculation_result.html',template = 'main/template.html',register_form = register_form,login_form = login_form)

@main.route('/sell',methods=['GET','POST'])
def sell():
    register_form = RegisterForm()
    login_form = LoginForm()
    communities = Community.query.all()
    if not session.get("USERNAME") is None:
        user = User.query.filter(User.username == session.get("USERNAME")).first()
        return render_template('main/sell.html',template='main/template_after_login.html',user=user,communities = communities)
    else:
        return render_template('main/sell_before_login.html',template='main/template.html',register_form = register_form,login_form = login_form)

@main.route('/handle_sell',methods=['POST'])
def handle_sell():
    user = User.query.filter(User.username == session.get("USERNAME")).first()
    form = request.form
    community_name = form['community']
    community = Community.query.filter(Community.id == community_id[community_name]).first()
    followers = 0
    price = form['price']
    square = form['square']
    bedroom = form['bedroom']
    livingroom = form['livingroom']
    kitchen = form['kitchen']
    bathroom = form['bathroom']
    construction_time = community.construction_time
    renovation = form['renovationCondition']
    buildingType = form['buildingType']
    buildingStructure = form['buildingStructure']
    subway = form['subway']
    fiveYearsProperty = form['fiveYearsProperty']
    district = community.district
    community_average = community.price
    town = community.town
    floorHeight = form['floorHeight']
    floorType = form['floorType']
    elevator = form['elevator']
    lng = community.lng
    lat = community.lat
    agent_id = 0
    status = 0

    new_property = Property(agent_id=agent_id,bathroom=bathroom,
                            bedroom=bedroom,lat=lat,lng=lng,
                            livingroom=livingroom,kitchen=kitchen,
                            town=town,district=district,
                            floorHeight=floorHeight,floorType=floorType,
                            communityAverage=community_average,fiveYearsProperty=fiveYearsProperty,
                            buildingStructure=buildingStructure,buildingType=buildingType,
                            renovationCondition=renovation,subway=subway,
                            constructionTime=construction_time,square=square,
                            price=int((int(price)*1000)/int(square)),elevator=elevator,followers=followers,community=community_name,owner_id=user.id,status = status)
    db.session.add(new_property)
    db.session.commit()
    
    return redirect(url_for('main.sell_result',_external=True))
    # return jsonify({'status':'success'})

@main.route('/main/sell_result',methods=['GET','POST'])
def sell_result():
    register_form = RegisterForm()
    login_form = LoginForm()
    if not session.get("USERNAME") is None:
        user = User.query.filter(User.username == session.get("USERNAME")).first()
        return render_template('main/sell_result.html',template = 'main/template_after_login.html',user=user)
    else:
        return # return redirect(url_for('main.sell'))

@main.route('/community_suggestion',methods=['POST'])
def community_suggestion():
    
    keyword = request.form['keyword']

    rank = process.extract(keyword, communities, limit=5)
    ranks = []
    for i in rank:
        ranks.append(i[0])

    return jsonify({"rank":ranks})

@main.route('/my_properties',methods=['GET','POST'])
def my_properties():
    user = User.query.filter(User.username == session.get("USERNAME")).first()
    if not user is None:
        page = int(request.args.get('page', 1))
        properties = Property.query.filter(Property.owner_id==user.id).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
        count = len(properties.items)
        if count == 0:
            return render_template('main/no_properties.html',user=user)
        else:
            return render_template('main/my_properties.html',user=user,house_paginate=properties)
    else:
        return redirect(url_for('main.index'))

@main.route('/my_favorites',methods=['GET','POST'])
def my_favorites():
    user = User.query.filter(User.username == session.get("USERNAME")).first()
    if not user is None:
        favorites = FavoriteProperty.query.filter(FavoriteProperty.user_id==user.id).all()
        property_ids = [i.property_id for i in favorites]
        page = int(request.args.get('page', 1))
        properties = Property.query.filter(Property.id.in_(property_ids)).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
        count = len(properties.items)
        if count == 0:
            return render_template('main/no_favorites.html',user=user)
        else:
            return render_template('main/my_favorites.html',user=user,house_paginate=properties,count=count)
    else:
        return redirect(url_for('main.index'))

@main.route('/handle_favorites',methods=['POST'])
def handle_favorites():
    user = User.query.filter(User.username == session.get("USERNAME")).first()
    user_id = user.id
    property_id = int(request.form['property_id'])
    property_ = Property.query.filter(Property.id==property_id).first()
    old_favorite = FavoriteProperty.query.filter(FavoriteProperty.property_id==property_id,FavoriteProperty.user_id==user_id).first()
    if old_favorite:
        print('delete the old one')
        property_.followers -= 1
        db.session.delete(old_favorite)
        db.session.commit()
        return jsonify({'status':'cancel'})
    else:
        new_favorite = FavoriteProperty(user_id=user_id,property_id=property_id)
        property_.followers += 1
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status':'add'})

@main.route('/agent_main/<service>',methods=['POST',"GET"])
def agent_main(service):
    agent = Agent.query.filter(Agent.username == session.get("AGENT")).first()
    page = int(request.args.get('page', 1))
    applications = Property.query.filter(Property.status==0).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
    on_sale = Property.query.filter(Property.status==1).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
    sold = Property.query.filter(Property.status==2).paginate(page, current_app.config["SQLALCHEMY_NUM_PER_PAGE"], False)
    if not session.get("AGENT") is None:
        if service == 'on_sale':
            if len(on_sale.items) == 0:
                return render_template('main/agent_main.html',agent=agent,web='main/agent_no_on_sale.html',service='on_sale')
            else:
                return render_template('main/agent_main.html',agent=agent,on_sale=on_sale,web='main/agent_on_sale.html',service='on_sale')
        elif service == 'sold':
            if len(sold.items) == 0:
                return render_template('main/agent_main.html',agent=agent,web='main/agent_no_sold.html',service='sold')
            else:
                return render_template('main/agent_main.html',agent=agent,sold=sold,web='main/agent_sold.html',service='sold')
        else:
            if len(applications.items) == 0:
                return render_template('main/agent_main.html',agent=agent,web='main/agent_no_application.html',service='application')
            else:
                return render_template('main/agent_main.html',agent=agent,applications=applications,web='main/agent_application.html',service='application')
    else:
        return redirect(url_for('main.index'))

@main.route('/handle_agent_logout', methods=['GET'])
def agent_logout():
    session.pop("AGENT", None)
    return redirect(url_for('main.index',_external=True))

@main.route('/agent_approve_application/<id>', methods=['GET'])
def agent_approve_application(id):
    agent = Agent.query.filter(Agent.username == session.get("AGENT")).first()
    if agent:
        property_ = Property.query.filter(Property.id==id).first()
        property_.status = 1
        property_.agent_id = agent.id
        print(agent.id)
        db.session.commit()
    else:
        return redirect(url_for('main.agent_login',_external=True))
    return redirect(request.referrer)

@main.route('/agent_delete_property/<id>', methods=['GET'])
def agent_delete_property(id):
    agent = Agent.query.filter(Agent.username == session.get("AGENT")).first()
    if agent:
        property_ = Property.query.filter(Property.id==id).first()
        db.session.delete(property_)
        db.session.commit()
    else:
        return redirect(url_for('main.agent_login',_external=True))

    return redirect(request.referrer)

@main.route('/agent_sold/<id>', methods=['GET'])
def agent_sold(id):
    agent = Agent.query.filter(Agent.username == session.get("AGENT")).first()
    if agent:
        property_ = Property.query.filter(Property.id==id).first()
        property_.status = 2
        db.session.commit()
    else:
        return redirect(url_for('main.agent_login',_external=True))

    return redirect(request.referrer)


@main.route('/help',methods=['GET','POST'])
def help_page():
    register_form = RegisterForm()
    login_form = LoginForm()
    communities = Community.query.all()
    if not session.get("USERNAME") is None:
        user = User.query.filter(User.username == session.get("USERNAME")).first()
        return render_template('main/help.html', template='main/template_after_login.html', user=user,
                               communities=communities)
    else:
        return render_template('main/help.html', template='main/template.html',
                               register_form=register_form, login_form=login_form)
