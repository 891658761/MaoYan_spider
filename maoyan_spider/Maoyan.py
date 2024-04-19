# -- coding: utf-8 --**
from spider_.movie_spider import Movie_spider
from spider_.comment_spider import Comment
from spider_.office_spider import Office

# 函数类对象生成
movie_ = Movie_spider()
comment_ = Comment()
office_ = Office()
# 主函数
def main():
    # 启用爬取评论
    # Comment.getCommentMain(comment_)
    # 启用爬取电影数据
    Movie_spider.getMovieMain(movie_)
    # 启用爬取资讯
    # Office.getOfficeMain(office_)
if __name__ == '__main__':
    main()