# WOS-spider
Python script to crawl Web of Science retrieved papers based on selenium package.\
基于selenium包，爬取Web of Science检索的论文信息的Python脚本

## 思路

这个爬虫的思路继承和脱胎自[CNKI知网爬虫 & Python](https://zhuanlan.zhihu.com/p/670809708?)。新版Web of Science并不像知网一样不需要账号也能检索，而Web of Science一般需要购买账号或者使用图书馆数据库转跳。因为多种多样的的进入方式只能通过手动处理，进而思考：我们是否可以中断程序手动控制浏览器，之后再把控制权交给程序进行？然后就有了这样的代码。

综上所述，这个爬虫有了以下提升：

- **检索方式：**能自己手动进行任意方式检索，只要最后能进入论文页面
- **速度：**使用BeautifulSoup对网页html处理为爬取数据，相比Selenium对每个数据抓取快得多
- **稳定性：**Web of Science在国内访问不稳定，因为[方式]的改变，可以在网页出现问题后手动解决，也可以从自定义页面开始爬取

## 实现

这个程序的主要逻辑是利用Selenium库自动化爬取Web of Science（WOS）网站上的论文详情信息，并将抓取的数据存储到一个CSV文件中。

1. 定义`parse_html`函数，接收一个HTML字符串作为参数。该函数通过BeautifulSoup解析HTML内容，提取出论文的相关信息（如标题、引用次数、地址/国家、期刊名等），并将这些信息存入一个字典中。同时，它还尝试从HTML中获取当前论文所在的页码。

2. 在主函数`__main__`部分：
   - 初始化Chrome浏览器驱动并打开指定的URL（Web of Science的基础搜索页面）。
   - 要求用户手动操作浏览器至论文详情页面。
   - 切换到论文详情页面对应的浏览器窗口。
   - 进入循环，每次循环处理一篇论文的详情页面：
     - 使用Selenium的WebDriverWait等待页面元素加载完成。
     - 获取页面的HTML源代码并传给`parse_html`函数处理，得到论文信息字典以及当前页码。
     - 将论文信息添加到一个pandas DataFrame中，如果索引已存在则更新数据，否则新增一行。
     - 每处理完一篇论文后，就将其数据保存到CSV文件中。
     - 尝试点击“下一页”按钮以滚动到下一篇文章的详情页面，若点击失败则提示用户手动解决可能的问题。
     - 添加暂停时间以等待页面加载。

3. 循环结束后，关闭浏览器驱动。

整个程序实现了自动遍历Web of Science论文详情页面，抽取关键信息，并将结果有序地保存在CSV文件中。

## 使用

### 环境

运行方式：脚本运行

本地环境：Python 3.11.5，selenium 4.15.2，pandas 2.0.3，beautifulsoup4 4.12.2

### 可变参数

```python
url_root = 'https://webofscience-clarivate-cn-s.era.lib.swjtu.edu.cn/wos/alldb/basic-search'
papers_need = 100000
file_path = 'result.csv'    
wait_time = 30
pause_time = 3
```

- `url_root`：是自动打开的网页（可以是任意网页，因为要手动操作）
- `papers_need`：自动停止爬取的页数
- `file_path`：爬取结果表格文件存储路径
- `wait_time`：等待网页某元素加载的时间（秒），可以缩短
- `pause_time`：每次翻页后的等待时间（秒），平衡速度和稳定性，可以缩短

### 使用步骤

1. 运行程序。会自动打开谷歌浏览器，（确保安装了谷歌**chromedriver**，可以参考[Selenium安装WebDriver最新Chrome驱动](https://blog.csdn.net/Z_Lisa/article/details/133307151)）

2. 手动操作。
   1. 进入Web of Science（新版界面），使用自己的方式进入（没有可以淘宝买账号）
   2. 通过自己想要的方式，选择想要的数据库，输入关键词，点击检索
   3. 点击第一篇文章，进入文章页面
3. 自动爬取。在程序终端输入任意键继续，程序会自动爬取页面信息，并存储在csv表格中。
4. *异常处理：网页访问异常，点击“后退”回到上个界面，再输入任意键继续，继续爬取。
