var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        orders: [],
        page: 1, // 当前页数
        page_size: 5, // 每页数量,
        count: 0,  // 总数量,
        ORDER_STATUS_ENUM: {
            1: "去支付",
            2: "待发货",
            3: "待收货",
            4: "去评价",
            5: "已完成",
            6: "已取消",
        },
        PAY_METHOD_ENUM: {
            1: "货到付款",
            2: "支付宝",
        }
    },
    computed: {
        total_page: function(){  // 总页数
            return Math.ceil(this.count/this.page_size);
        },
        next: function(){  // 下一页
            if (this.page >= this.total_page) {
                return 0;
            } else {
                return this.page + 1;
            }
        },
        previous: function(){  // 上一页
            if (this.page <= 0 ) {
                return 0;
            } else {
                return this.page - 1;
            }
        },
        page_nums: function(){  // 页码
            // 分页页数显示计算
            // 1.如果总页数<=5
            // 2.如果当前页是前3页
            // 3.如果当前页是后3页,
            // 4.既不是前3页，也不是后3页
            var nums = [];
            if (this.total_page <= 5) {
                for (var i=1; i<=this.total_page; i++){
                    nums.push(i);
                }
            } else if (this.page <= 3) {
                nums = [1, 2, 3, 4, 5];
            } else if (this.total_page - this.page <= 2) {
                for (var i=this.total_page; i>this.total_page-5; i--) {
                    nums.push(i);
                }
            } else {
                for (var i=this.page-2; i<this.page+3; i++){
                    nums.push(i);
                }
            }
            return nums;
        }
    },
    mounted: function(){
        this.get_orders();
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 点击页数
        on_page: function(num){
            if (num != this.page){
                this.page = num;
                this.get_orders();
            }
        },
        // 获取订单数据
        get_orders: function () {
            axios.get(this.host+'/orders/', {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    params: {
                        page: this.page,
                        page_size: this.page_size
                    },
                    responseType: 'json'
                })
                .then(response => {
                    this.count = response.data.count;
                    this.orders = response.data.results;
                    for(var i=0; i<this.orders.length; i++){
                        for(var j=0; j<this.orders[i].skus.length; j++){
                            var order = this.orders[i];
                            var name = order.skus[j].sku.name;
                            if (name.length >= 25) {
                                this.orders[i].skus[j].sku.name = name.substring(0, 25) + '...';
                            }
                            this.orders[i].skus[j].amount = (parseFloat(order.skus[j].price) * order.skus[j].count).toFixed(2);
                            this.orders[i].status_name = this.ORDER_STATUS_ENUM[order.status];
                            this.orders[i].pay_method_name = this.PAY_METHOD_ENUM[order.pay_method];
                        }
                    }
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        },
        // 订单操作
        on_operate_order: function (index) {
            var order = this.orders[index];
            // 去支付
            if (order.status===1) {
                axios.get(this.host+'/orders/'+order.order_id+'/payment/', {
                        headers: {
                            'Authorization': 'JWT ' + this.token
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        // 跳转到支付宝支付
                        location.href = response.data.alipay_url;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    })
            }
            // 去评价
            else if (order.status === 4) {
                location.href = '/goods_judge.html?order_id=' + order.order_id;
            }
        }
    }
});