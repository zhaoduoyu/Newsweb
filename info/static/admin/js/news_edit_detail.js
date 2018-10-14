function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_edit").submit(function (e) {
        e.preventDefault()
        // 新闻编辑提交
        $(this).ajaxSubmit({
            url:"/admin/news_edit_detail",
            type:"post",
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (resp) {
                if (resp.errno == "0"){
                    window.parent.location.href = '/admin/news_edit'
                }else{
                    alert(resp.errmsg)
                }
            }
        })
    })
})

// 点击取消，返回上一页
function cancel() {
    history.go(-1)
}