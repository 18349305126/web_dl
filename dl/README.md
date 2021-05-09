# 简介

待补充

# Install

```
pip install -r requirements.txt
```

# Usage

在项目根目录下运行：

```
python manage.py runserver
```

# 项目结构

- webdl: django project 以及配置文件
- api: django app，存放业务逻辑，控制层在 `views.py`，服务层在 `services.py`，`utils`下为原本的转换代码
