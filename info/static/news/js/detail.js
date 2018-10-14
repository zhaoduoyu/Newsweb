function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    })

    // 收藏
    $(".collection").click(function () {
        var news_id = $(this).attr('news_id')
        var params = {
            "news_id": news_id,
            "action":"collect"
        }
        $.ajax({
            url:"/news_collect",
            type:"POST",
            data:JSON.stringify(params),
            contentType:"application/json",
            headers:{"X-CSRFToken":getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno==0){
                    $('.collection').hide()
                    $(".collected").show()
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

    // 取消收藏
    $(".collected").click(function () {
        var news_id = $(this).attr('news_id')
        var params = {
            "news_id": news_id,
            "action":"cancel_collect"
        }
        $.ajax({
            url:"/news_collect",
            type:"POST",
            data:JSON.stringify(params),
            contentType:"application/json",
            headers:{"X-CSRFToken":getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno==0){
                    $(".collected").hide()
                    $('.collection').show()
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

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();

    })

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            }else {
                $this.addClass('has_comment_up')
            }
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            alert('回复评论')
        }
    })

        // 关注当前新闻作者
    $(".focus").click(function () {
        var user_id = $(this).attr('user_id')
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
                    $(".focus").hide()
                    $('.focused').show()
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
                    $(".focused").hide()
                    $('.focus').show()
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