var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        is_show_waiting: true,

        error_password: false,
        error_phone: false,
        error_image_code: false,
        error_sms_code: false,
        error_image_code_message: '',
        error_phone_message: '',
        error_sms_code_message: '',

        image_code_id: '', // 图片验证码id
        image_code_url: '',

        sms_code_tip: '获取短信验证码',
        sending_flag: false, // 正在发送短信标志

        password: '',
        mobile: '',
        image_code: '',
        sms_code: '',
        access_token: ''
    },
    mounted: function(){
        // 从路径中获取微博重定向返回的code
        var code = this.get_query_string('code');
        axios.get(this.host + '/oauth/sina/user/?code=' + code, {
                responseType: 'json',
            })
            .then(response => {
                if (response.data.user_id){
                    // 用户已绑定
                    sessionStorage.clear();
                    localStorage.clear();
                    localStorage.user_id = response.data.user_id;
                    localStorage.username = response.data.username;
                    localStorage.token = response.data.token;

                    // 从路径中取出state,引导用户进入登录成功之后的页面
                    var state = this.get_query_string('state');
                    location.href = state;
                } else {
                    // 用户未绑定
                    this.access_token = response.data.access_token;
                    this.generate_image_code();
                    this.is_show_waiting = false;
                }
            })
            .catch(error => {
                console.log(error.response.data);
                alert('服务器异常');
            })
    },
    methods: {
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        // 生成uuid
        generate_uuid: function(){
            var d = new Date().getTime();
            if(window.performance && typeof window.performance.now === "function"){
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c =='x' ? r : (r&0x3|0x8)).toString(16);
            });
            return uuid;
        },
        // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
        generate_image_code: function(){
            // 生成一个编号
            // 严格一点的使用uuid保证编号唯一， 不是很严谨的情况下，也可以使用时间戳
            this.image_code_id = this.generate_uuid();

            // 设置页面中图片验证码img标签的src属性
            this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
        },
        check_pwd: function (){
            var len = this.password.length;
            if(len<8||len>20){
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_phone: function (){
            var re = /^1[345789]\d{9}$/;
            if(re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone_message = '您输入的手机号格式不正确';
                this.error_phone = true;
            }
        },
        check_image_code: function (){
            if(!this.image_code) {
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function(){
            if(!this.sms_code){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        // 发送手机短信验证码
        send_sms_code: function(){
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            // 校验参数，保证输入框有数据填写
            this.check_phone();
            this.check_image_code();

            if (this.error_phone == true || this.error_image_code == true) {
                this.sending_flag = false;
                return;
            }

            // 向后端接口发送请求，让后端发送短信验证码
            axios.get(this.host + '/sms_codes/' + this.mobile + '/?text=' + this.image_code+'&image_code_id='+ this.image_code_id, {
                    responseType: 'json'
                })
                .then(response => {
                    // 表示后端发送短信成功
                    // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
                    var num = 60;
                    // 设置一个计时器
                    var t = setInterval(() => {
                        if (num == 1) {
                            // 如果计时器到最后, 清除计时器对象
                            clearInterval(t);
                            // 将点击获取验证码的按钮展示的文本回复成原始文本
                            this.sms_code_tip = '获取短信验证码';
                            // 将点击按钮的onclick事件函数恢复回去
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // 展示倒计时信息
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000, 60)
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        this.error_image_code_message = '图片验证码有误';
                        this.error_image_code = true;
                    } else {
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                })
        },
        // 保存
        on_submit: function() {
            this.check_pwd();
            this.check_phone();
            this.check_sms_code();

            if (this.error_password == false && this.error_phone == false && this.error_sms_code == false) {
                axios.post(this.host + '/oauth/sina/user/', {
                    password: this.password,
                    mobile: this.mobile,
                    sms_code: this.sms_code,
                    access_token: this.access_token
                }, {
                    responseType: 'json',
                })
                    .then(response => {
                        // 记录用户登录状态
                        sessionStorage.clear();
                        localStorage.clear();
                        localStorage.token = response.data.token;
                        localStorage.user_id = response.data.user_id;
                        localStorage.username = response.data.username;
                        location.href = '/';
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_sms_code_message = error.response.data.message;
                            this.error_sms_code = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        }
    }
});