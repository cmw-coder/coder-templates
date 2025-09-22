.. _topics-WEB测试:


WEB测试
================
WEB自动化测试是指使用自动化测试工具和脚本来模拟用户的操作，并验证Web应用程序是否按照预期进行操作的过程。 Web自动化测试是通过模拟用户操作网页元素（如文本框，图像，按钮等）来实现测试的过程。

框架提供的WEB自动化基于chrome浏览器和selenium元素定位的方式提供Webtest类，该类提供6个基础接口，主要原因是各产品的WEB内容各不相同，框架无法提供统一的接口，用户可基于这6个接口开发适合自己产品的web自动化接口，用户开发的这些接口随脚本工程一同维护。

Webtest类默认隐式等待时间为5s，用户可通过类属性 ``implicitly_wait_time`` 进行设置，基础接口介绍详见下文。

----------------
基础接口介绍
----------------

``OpenBrowser`` 用于打开浏览器，支持2个参数：

- url: 要打开的地址，必选参数，字符串类型
- title: 打开url后页面的名称，必选参数，字符串类型


``GetText`` 用于获取元素对象的文本信息，支持3个参数：

- location: 定位元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``Click`` 用于点击元素，支持3个参数：

- location: 定位元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``DoubleClick`` 用于双击元素，支持3个参数：

- location: 定位元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``Input`` 用于输入框输入文本，支持4个参数：

- input_text : 输入框输入文本，必选参数，字符串类型
- location: 定位元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``Select`` 用于选择文本，支持4个参数：

- select_value : 选择文本，必选参数，单选为字符串类型，多选为列表
- location: 定位元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``HandlePopup`` 用于关闭弹出窗口，支持2个参数：

- popup : 窗口类型，只支持alert、confirm、prompt三种类型的窗口，必选参数，为字符串类型
- prompt: prompt类型时有效，为提示窗口待输入信息，可选参数，为字符串类型


``UploadFile`` 用于上传文件，支持47参数：

- filie : 文件的绝对路径，必选参数，为字符串类型
- location: 定位上传区元素的路径或查找到的元素对象，必选参数，字符串类型或者是已查找到的元素对象
- method: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型
- location2: 定位确认区元素的路径或查找到的元素对象，可选参数，字符串类型或者是已查找到的元素对象，为空时，表示只输入上传的文件，不进行确认操作
- method2: 用户指定查找元素的方法, 可指定为:id/name/class_name/tag_name/link_text/partial_link_text/xpath/css_selector/locate_with, 默认为xpath，可选参数，字符串类型
- index2: 根据location查找到的第几个为目标元素，默认为0，可选参数，字符串类型


``screen_shot`` 用于截图，支持1个参数：

- action : 用户自定义是否截图，默认为False，只在接口报错之处进行截图，可选参数，当设为True时，默认每个Click/Input/Select都会进行截图


``CloseBrowser`` 用于测试结束后关闭浏览器


``其它``  除了上述方法外，Webtest()对象继承了webdriver对象的所有方法，如find_element、get等。开发脚本时，如遇到基础接口不满足时，可以直接使用webdriver的方法。


使用示例如下：

.. code-block:: python
    :linenos:

    # 先查找脚本中设置的chromedriver.exe路径，如果不存在，则查找RDTestClientData\Common\tools\Python38路径
    #  如果可以找到chromedriver.exe，则用其启动浏览器，如果失败，则尝试自动下载
    #  如果仍找不到chromedriver.exe，则尝试自动下载
    #  如果下载失败，则提示用户手工下载与浏览器版本匹配的chromedriver.exe
    web_driver = Webtest()
    
    # 支持对web自动化过程中的截图和下载文件保存位置进行自定义设置，需要在OpenBrowser前对属性 screenpath 和 downloads_path 赋值
    # 不设置时，默认截图和下载文件保存位置为脚本日志所在同路径，文件夹名称为5位随机码的文件夹中，随机码与脚本执行时日志文件名中包含的随机码一致
    web_driver.screenpath = "D:/SCREEN"
    web_driver.downloads_path = "D:/DOWNPATH"
    # 打开测试仪前端页面
    web_driver.OpenBrowser(f"http://www.baidu.com","百度一下，你就知道")
    web_driver.Input('新华三', 'kw', 'id')
    web_driver.Click('su', 'id')
    # 关闭页面
    web_driver.CloseBrowser()



----------------
webdriver下载
----------------
selenium元素定位方法可基于不同的浏览器，pyPilot框架的web自动化基于chrome浏览器开发，因此需要下载chromedriver

chromedriver的下载地址： `driver下载地址 <https://chromedriver.storage.googleapis.com/index.html>`_ ，如果此链接没有找到期望的版本，用户也可自行在网上搜索下载

.. note:: chromedriver的版本需要与执行机chrome的版本一致，查看chrome版本的方法此处不再赘述