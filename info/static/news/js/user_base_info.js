function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".base_info").submit(function (e) {
        e.preventDefault()
        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // 修改用户信息接口
        // $('#csrf_token').attr("value", getCookie('csrf_token'))
        var params = {
            'signature':signature,
            'nick_name':nick_name,
            'gender':gender
        }
        $.ajax({
            url:"/user/base_info",
            type:"post",
            data:JSON.stringify(params),
            contentType:"application/json",
            headers:{"X-CSRFToken":getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno==0){
                    window.parent.location.reload()
                }
                else if (resp.errno==4102){
                    $('.login_form_con').show();
                }
                else{
                    alert(resp.errmsg)
                }
            }
        })

    })
})