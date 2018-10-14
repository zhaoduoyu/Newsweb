 var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {

    // {#  默认加载首页 #}
    updateNewsData()
    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid
            $('#cont_ul').html('')
            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // 判断页数，去更新新闻数据
            // alert(1)
            updateNewsData()
        }
    })
})

function updateNewsData() {
    // 更新新闻数据
    var params = {
        'page':cur_page,
        'curentCid':currentCid
    }
    cur_page += 1
    $.ajax({
        url:'/update_news',
        data:JSON.stringify(params),
        type:'post',
        contentType:'application/json',
        headers:{'X-CSRFToken':getCookie("csrf_token")},
        // datatype:'json',
        success:function (data) {
            var str = ''
            data = eval(data)
            console.log(data)
            for(i=0; i< data.length; i++){
                str += '<li> <a href="#" class="news_pic fl"><img src="'
                    +data[i].index_image_url+'"></a> <a href="/detail?id='
                    +data[i].id+'" class="news_title fl">'
                    +data[i].title+'</a> <a href="#" class="news_detail fl">'
                    +data[i].digest+'</a> <div class="author_info fl"> <div class="source fl">来源：'
                    +data[i].source+' </div> <div class="time fl">'
                    +data[i].create_time+'</div> </div> </li>'

            }
            $('#cont_ul').append(str)

        },
        error:function () {
            alert('failed')
        }
    })
}
