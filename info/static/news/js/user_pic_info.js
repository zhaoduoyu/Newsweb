function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault()

        //上传头像
        // var avatar = $('.input_file').val()
        // console.log(avatar)
        $(this).ajaxSubmit({
            url:"/user/pic_info",
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