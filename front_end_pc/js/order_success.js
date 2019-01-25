var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        order_id: '',
        amount: 0,
        pay_method: '',
    },
    computed: {
        operate: function(){
            if (this.pay_method==1){
                return '继续购物';
            } else {
                return '去支付';
            }
        }
    },
    mounted: function(){
        this.order_id = this.get_query_string('order_id');
        this.amount = this.get_query_string('amount');
        this.pay_method = this.get_query_string('pay');
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        next_operate: function(){
            if (this.pay_method == 1) {
                location.href = '/index.html';
            } else {
                // 发起支付
                axios.get(this.host+'/orders/'+this.order_id+'/payment/', {
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
        }
    }
});