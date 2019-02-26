var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        tab_content: {
            detail: true,
            pack: false,
            comment: false,
            service: false
        },
        sku_id: '',
        sku_count: 1,
        sku_price: price,
        cart_total_count: 0, // 购物车总数量
        cart: [], // 购物车数据
        hots: [], // 热销商品
        cat: cat, // 商品类别
        comments: [], // 评论信息
        score_classes: {
            1: 'stars_one',
            2: 'stars_two',
            3: 'stars_three',
            4: 'stars_four',
            5: 'stars_five',
        }
    },
    computed: {
        sku_amount: function(){
            return (this.sku_price * this.sku_count).toFixed(2);
        }
    },
    mounted: function(){
        // 添加用户浏览历史记录
        this.get_sku_id();
        if (this.user_id) {
            axios.post(this.host+'/browse_histories/', {
                sku_id: this.sku_id
            }, {
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
        }
        this.get_cart();
        this.get_hot_goods();
        this.get_comments();
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 控制页面标签页展示
        on_tab_content: function(name){
            this.tab_content = {
                detail: false,
                pack: false,
                comment: false,
                service: false
            };
            this.tab_content[name] = true;
        },
        // 从路径中提取sku_id
        get_sku_id: function(){
            var re = /^\/goods\/(\d+).html$/;
            this.sku_id = document.location.pathname.match(re)[1];
        },
        // 减小数值
        on_minus: function(){
            if (this.sku_count > 1) {
                this.sku_count--;
            }
        },
        // 添加购物车
        add_cart: function(){
            axios.post(this.host+'/cart/', {
                    sku_id: parseInt(this.sku_id),
                    count: this.sku_count
                }, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    alert('添加购物车成功');
                    this.cart_total_count += response.data.count;
                })
                .catch(error => {
                    if ('non_field_errors' in error.response.data) {
                        alert(error.response.data.non_field_errors[0]);
                    } else {
                        alert('添加购物车失败');
                    }
                    console.log(error.response.data);
                })
        },
        // 获取购物车数据
        get_cart: function(){
            axios.get(this.host+'/cart/', {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    this.cart = response.data;
                    this.cart_total_count = 0;
                    for(var i=0;i<this.cart.length;i++){
                        if (this.cart[i].name.length>25){
                            this.cart[i].name = this.cart[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.cart[i].count;

                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 获取热销商品数据
        get_hot_goods: function(){
            axios.get(this.host+'/categories/'+this.cat+'/hotskus/', {
                    responseType: 'json'
                })
                .then(response => {
                    this.hots = response.data;
                    for(var i=0; i<this.hots.length; i++){
                        this.hots[i].url = '/goods/' + this.hots[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 获取商品评价信息
        get_comments: function(){
            axios.get(this.host+'/skus/'+this.sku_id+'/comments/', {
                    responseType: 'json'
                })
                .then(response => {
                    this.comments = response.data;
                    for(var i=0; i<this.comments.length; i++){
                        this.comments[i].score_class = this.score_classes[this.comments[i].score];
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
    }
});