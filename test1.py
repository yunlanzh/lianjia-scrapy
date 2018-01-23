#_*_coding:utf-8_*_

# 导入开发模块
import requests
# 用于解析html数据的框架
from bs4 import BeautifulSoup
# 用于操作excel的框架
import xlwt

# 创建一个工作
book = xlwt.Workbook()
# 向表格中增加一个sheet表，sheet1为表格名称 允许单元格覆盖
sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)

# 指定爬虫所需的上海各个区域名称
citys = ['pudongxinqu', 'minhang', 'baoshan', 'xuhui', 'putuo', 'yangpu', 'changning',
         'huangpu', 'jinan', 'zhabei', 'hongkou']


def getHtml(city):
    url = 'http://sh.lianjia.com/ershoufang/%s/' % city
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    request = requests.get(url=url, headers=headers)
    # 获取源码内容比request.text好，对编码方式优化好
    respons = request.content
    # 使用bs4模块，对响应的链接源代码进行html解析，后面是python内嵌的解释器，也可以安装使用lxml解析器
    soup = BeautifulSoup(respons, 'html.parser')
    # 获取类名为c-pagination的div标签，是一个列表
    page = soup.select('div .c-pagination')[0]
    # 如果标签a标签数大于1，说明多页，取出最后的一个页码，也就是总页数
    if len(page.select('a')) > 1:
        alist = int(page.select('a')[-2].text)
    else:  # 否则直接取出总页数
        alist = int(page.select('span')[0].text)
    # 调用方法解析每页数据
    saveData(city, url, alist + 1)
    # for i in range(1,alist + 1):
    #     urlStr = '%sd%s' % (url,i)


# 调用方法解析每页数据，并且保存到表格中
def saveData(city, url, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    for i in range(1, page):
        html = requests.get(url='%sd%s' % (url, i), headers=headers).content
        soup = BeautifulSoup(html, 'html.parser')
        infos = soup.select('.js_fang_list')[0].select('li')
        for info in infos:
            # print '*'*50
            des = info.find(
                'a', class_="text link-hover-green js_triggerGray js_fanglist_title").text
            dd = info.find('div', class_='info-table')
            nameInfo = dd.find('a', class_='laisuzhou')
            name = nameInfo.text  # 每套二手房的小区名称

            fangL = dd.find('span').contents[-1].strip().split('|')
            room_type = fangL[0].strip()  # 每套二手房的户型
            size = fangL[1].strip()  # 每套二手房的面积
            if len(fangL[2].split('/')) == 2:
                region = fangL[2].split('/')[0].strip()  # 每套二手房所属的区域
                loucheng = fangL[2].split('/')[1].strip()  # 每套二手房所在的楼层
            else:
                region = ''  # 每套二手房所属的区域
                loucheng = fangL[2].strip()  # 每套二手房所在的楼层
            if len(fangL) != 4:
                chaoxiang = '*'
            else:
                chaoxiang = fangL[3].strip()  # 每套二手房的朝向

            timeStr = info.find(
                'span', class_='info-col row2-text').contents[-1].strip().lstrip('|')
            builtdate = timeStr  # 每套二手房的建筑时间

            # 每套二手房的总价
            price = info.find(
                'span', class_='total-price strong-num').text.strip() + u'万'
            # 每套二手房的平方米售价
            jun = info.find('span', class_='info-col price-item minor').text
            price_union = jun.strip()
            # 一定要声明使用全局的row变量，否则会报错，说定义前使用了该变量
            global row
            # 把数据写入表中，row:行数 第二个参数：第几列 第三个参数：写入的内容
            sheet.write(row, 0, des)
            sheet.write(row, 1, name)
            sheet.write(row, 2, room_type)
            sheet.write(row, 3, size)
            sheet.write(row, 4, region)
            sheet.write(row, 5, loucheng)
            sheet.write(row, 6, chaoxiang)
            sheet.write(row, 7, price)
            sheet.write(row, 8, price_union)
            sheet.write(row, 9, builtdate)
            # 每次写完一行，把行索引进行加一
            row += 1
            # with open('%s.csv' % city,'ab') as fd:
            #     allStr = ','.join([name,room_type,size,region,loucheng,chaoxiang,price,price_union,builtdate])+'\n'
            #     fd.write(allStr.encode('utf-8'))


# 判断当前运行的脚本是否是该脚本，如果是则执行
# 如果有文件xxx继承该文件或导入该文件，那么运行xxx脚本的时候，这段代码将不会执行
if __name__ == '__main__':
    # getHtml('jinshan')
    row = 0
    for i in citys:
        getHtml(i)
    # 最后执行完了保存表格，参数为要保存的路径和文件名，如果不写路径则默然当前路径
    book.save('lianjia-shanghai.xls')
