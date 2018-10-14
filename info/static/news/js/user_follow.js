function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    // $(".focused").click(function () {
    //     // 关注当前新闻作者
    // })
    //
    $(".focus").click(function () {
        var user_id = $(this).attr('user_id')
        $(this).attr("id", "focus")
        $(this).next().attr("id", "focused")
        var params = {
            "user_id": user_id,
            "action":"follow"
        }
        $.ajax({
            url:"/followed_user",
            type:"POST",
            data:JSON.stringify(params),
            contentType:"application/json",
            headers:{"X-CSRFToken":getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno==0){
                    // window.location.reload()
                    $("#focus").hide().attr("id", "")
                    $("#focused").show().attr("id", "")
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

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        var user_id = $(this).attr('user_id')
        $(this).attr("id", "focused")
        $(this).prev().attr("id", "focus")
        var params = {
            "user_id": user_id,
            "action":"unfollow"
        }
        $.ajax({
            url:"/followed_user",
            type:"POST",
            data:JSON.stringify(params),
            contentType:"application/json",
            headers:{"X-CSRFToken":getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno==0){
                    // window.location.reload()
                    $("#focused").hide().attr("id", "")
                    $("#focus").show().attr("id", "")

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