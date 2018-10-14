function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // 修改密码
        $(this).ajaxSubmit({
            url:"/user/user_pass_info",
            type:"post",
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno == "0"){
                    window.parent.location.reload()
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
})