var vm = new Vue({
	el: '#app',
	data: {
		error_name: false,
		error_password: false,
		error_check_password: false,
		error_phone: false,
		error_allow: false,
		error_sms_code: false,

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
				this.error_phone = true;
			}
		},
		check_sms_code: function(){
			if(!this.sms_code){
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
