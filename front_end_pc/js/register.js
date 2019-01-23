var vm = new Vue({
    el: '#app',
    data: {
        host: host,

        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_sms_code: false,
        error_name_message: '',
        error_phone_message: '',
        error_sms_code_message: '',

        sms_code_tip: '获取短信验证码',
        sending_flag: false, // 正在发送短信标志

        username: '',
        password: '',
        password2: '',
        mobile: '',
        sms_code: '',
        allow: false
    },
    methods: {
        check_username: function (){
            var len = this.username.length;
            if(len<5||len>20) {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            } else {
                this.error_name = false;
            }

        },
        check_pwd: function (){
            var len = this.password.length;
            if(len<8||len>20){
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function (){
            if(this.password!=this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
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
        check_sms_code: function(){
            if(!this.sms_code){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_allow: function(){
            if(!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
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

            if (this.error_phone == true) {
                this.sending_flag = false;
                return;
            }

            // 向后端接口发送请求，让后端发送短信验证码
            axios.get(this.host + '/sms_codes/' + this.mobile + '/', {
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
                        this.error_sms_code_message = error.response.data.message;
                        this.error_sms_code = true;
                    } else {
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                })
        },
        // 注册
        on_submit: function(){
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();

        }
    }
});