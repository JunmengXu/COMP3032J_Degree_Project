//Gaode Map, Asynchronous loading
function onApiLoaded() {
    //获取房子的坐标（百度坐标）
    var houselng = document.getElementById('house-lng').textContent;
    var houselat = document.getElementById('house-lat').textContent;
    var rightLnglat = [houselng, houselat];

    // // 坐标转换,百度坐标规范 转 高德地图坐标规范
    // AMap.convertFrom([houselng, houselat], 'baidu', function (status, result) {
    //     if (result.info === 'ok') {
    //         rightLnglat = result.locations[0];
    //     }
    // });

    //获取按钮控件
    var cinemaButton = document.getElementById('cinema');
    var cateringButton = document.getElementById('catering');
    var hospitalButton = document.getElementById('hospital');
    var hotelButton = document.getElementById('hotel');
    var shoppingButton = document.getElementById('shopping');
    var businessButton = document.getElementById('business');

    //构建地图
    var map = new AMap.Map('map', {
        center: rightLnglat,
        zoom: 13,
        lang: "en" //可选值：en，zh_en, zh_cn
    });

    AMap.service(["AMap.PlaceSearch"], function() {
        //构造地点查询类
        var cinema = new AMap.PlaceSearch({
            type: '电影院', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });
        var catering = new AMap.PlaceSearch({
            type: '餐饮', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });
        var hotel = new AMap.PlaceSearch({
            type: '住宿服务', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });
        var shopping = new AMap.PlaceSearch({
            type: '购物服务', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });
        var hospital = new AMap.PlaceSearch({
            type: '医疗保健服务', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });
        var business = new AMap.PlaceSearch({
            type: '公司企业', // 兴趣点类别
            city: "010", // 兴趣点城市
            citylimit: true,  //是否强制限制在设置的城市内搜索
            map: map, // 展现结果的地图实例
            autoFitView: true, // 是否自动调整地图视野使绘制的 Marker点都处于视口的可见范围
            lang: "en"
        });

        //构造按钮点击事件
        AMap.event.addDomListener(cinemaButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            cinema.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_film.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });

        AMap.event.addDomListener(cateringButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            catering.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_catering.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });

        AMap.event.addDomListener(hotelButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            hotel.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_hotel.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });

        AMap.event.addDomListener(shoppingButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            shopping.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_shop.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });

        AMap.event.addDomListener(hospitalButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            hospital.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_health.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });

        AMap.event.addDomListener(businessButton, 'click', function (e) {
            map.clearMap();
            map.add(m2);
            business.searchNearBy('', rightLnglat, 1000, function(status, result) {
                var pois = result.poiList.pois;
                    for(var i = 0; i < pois.length; i++){
                        var poi = pois[i];
                        var marker = [];
                        marker[i] = new AMap.Marker({
                            position: poi.location,   // 经纬度对象，也可以是经纬度构成的一维数组[116.39, 39.9]
                            title: poi.name,
                            icon: '../../static/images/mapicon/icon_business.png',
                        });
                        //点击跳转至高德地图界面
                        marker[i].id= poi.id;
                        marker[i].name = poi.name;
                        marker[i].on('click',function(){
                            map.poiOnAMAP({
                                name:this.name,
                                location:this.getPosition(),
                                id:this.id
                            })
                        })
                        // 将创建的点标记添加到已有的地图实例：
                        map.add(marker[i]);
                    }
            });
        });
    });
    //创建搜索插件
    map.plugin(["AMap.ToolBar", 'AMap.Autocomplete', 'AMap.PlaceSearch'], function () {
        map.addControl(new AMap.ToolBar());
        // 实例化Autocomplete
        var autoOptions = {
            city: '北京',
            input: 'map_search',
            citylimit: true,
            lang:"en"
        }
        var autoComplete = new AMap.Autocomplete(autoOptions);

        var placeSearch = new AMap.PlaceSearch({
            city: '北京',
            map: map,
            lang: "en"
        })
    //     // var cinema = new AMap.PlaceSearch({
    //     //     city: '北京',
    //     //     map: map,
    //     //     type: '电影院'
    //     // })
    //     var catering = new AMap.PlaceSearch({
    //         city: '北京',
    //         map: map,
    //         type: '餐饮',
    //     })
    //     var hotel = new AMap.PlaceSearch({
    //         city: '北京',
    //         map: map,
    //         type: '住宿服务',
    //     })
    //     var shopping = new AMap.PlaceSearch({
    //         city: '北京',
    //         map: map,
    //         type: '购物服务',
    //     })
    //     var hospital = new AMap.PlaceSearch({
    //         city: '北京',
    //         map: map,
    //         type: '医疗保健服务',
    //     })
    //     var business = new AMap.PlaceSearch({
    //         city: '北京',
    //         map: map,
    //         type: '公司企业'
    //     })
    //
        AMap.event.addListener(autoComplete, 'select', function (e) {
            //TODO 针对选中的poi实现自己的功能
            placeSearch.search(e.poi.name)
        })
    //     AMap.event.addDomListener(cateringButton, 'click', function (e) {
    //          map.clearMap();
    //         catering.search()
    //     })
    //     AMap.event.addDomListener(shoppingButton, 'click', function (e) {
    //          map.clearMap();
    //         shopping.search()
    //     })
    //     AMap.event.addDomListener(hospitalButton, 'click', function (e) {
    //         map.clearMap();
    //         hospital.search()
    //     })
    //     AMap.event.addDomListener(businessButton, 'click', function (e) {
    //         map.clearMap();
    //         business.search()
    //     })
    //     AMap.event.addDomListener(hotelButton, 'click', function (e) {
    //         map.clearMap();
    //         hotel.search()
    //     })
    });
    //添加marker
    m2 = new AMap.Marker({
        position: rightLnglat,
        icon: '../../static/images/mapicon/icon_house.png'
    });
    map.add(m2);
    // 设置标签
    m2.setLabel({
        anchor: 'center', //设置锚点
        offset: new AMap.Pixel(0,0), //设置偏移量
        content: "Here is the house location",
        direction: 'right' //设置文本标注方位
    });
    var circle = new AMap.Circle({
        center: [houselng, houselat],  // 圆心位置
        radius: 1000, // 圆半径
        fillColor: 'blue',   // 圆形填充颜色
        fillOpacity: 0.3,
        bubble: true,
        strokeColor: '#fff', // 描边颜色
        strokeWeight: 2, // 描边宽度
    });
    if(AMap.UA.mobile){
        document.getElementsByClassName('info')[0].style.display='none';
    }
    //map.add(circle);

    map.add(circle);
    // map.add(marker);
    //绑定按钮事件，改变地图中心点
    document.querySelector("#back-house-btn").onclick = function() {
      map.setZoomAndCenter(15,rightLnglat); //设置地图中心点
      log.info(`已复位`);
    }
}


//异步加载
var url = 'https://webapi.amap.com/maps?v=1.4.15&key=d69b952ebb1b2dd61d42619428f5063e&callback=onApiLoaded';
var jsapi = document.createElement('script');
jsapi.charset = 'utf-8';
jsapi.src = url;
document.head.appendChild(jsapi);

//    房子图片展示逻辑
var round1 = Math.round(Math.random() * 10) + 1;
var round2 = Math.round(Math.random() * 10) + 1;
// console.log(round1);
$(".room1g").attr("src", "../../static/images/renovationCondition/good/room1/" + round1 + ".jpg");
$(".room2g").attr("src", "../../static/images/renovationCondition/good/room2/" + round2 + ".jpg");
$(".room1r").attr("src", "../../static/images/renovationCondition/rough/room1/" + round1 + ".jpg");
$(".room2r").attr("src", "../../static/images/renovationCondition/rough/room2/" + round2 + ".jpg");