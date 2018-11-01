# internal export
from crawler import *

# Test 1 to get best picture and article title
soup = simple_get("http://tieba.baidu.com/p/5858562576")
print("Best Picture ==>",get_pictures(soup))
print("Article Title ==>",get_title(soup))

# Test 2 to get best picture and article title
soup = simple_get("http://www.nba.com/")
print("Best Picture ==>",get_pictures(soup))
print("Article Title ==>",get_title(soup))

# Test the recommend_article function
start = time.time()
print("Recommended Article Title ==>", recommend_article('https://www.cbnweek.com/','科技')) # https://www.cbnweek.com/
'{0} seconds taken to recommend this article from given site with given tag'.format(time.time()-start)