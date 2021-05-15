const Mock = require('mockjs')

const history = Mock.mock({
  'items|30': [{
    id: '@id',
    title: '@sentence(10, 20)',
    'status|1': ['任务结束', '执行中', '任务失败'],
    author: 'name',
    display_time: '@datetime',
    pageviews: '@integer(300, 5000)'
  }]
})

const List = []
const count = 100

const baseContent = '测试数据'
const image_uri = 'https://wpimg.wallstcn.com/e4558086-631c-425c-9430-56ffb46e70b3'

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    id: '@increment',
    timestamp: +Mock.Random.date('T'),
    author: '@first',
    datasetList: '@last',
    reviewer: '@first',
    title: '@title(2, 4)',
    content_short: 'mock data',
    content: baseContent,
    forecast: '@float(0, 100, 2, 2)',
    importance: '@integer(1, 3)',
    'type|1': ['CN', 'US', 'JP', 'EU'],
    'status|1': ['published', 'draft', 'deleted'],
    display_time: '@datetime',
    comment_disabled: true,
    pageviews: '@integer(300, 5000)',
    image_uri,
    platforms: ['a-platform']
  }))
}

const ModelList = {}

for (let i = 0; i < count; i++) {
  const tmp = []
  for (let i = 0; i < 3; i++) {
    tmp.push(Mock.mock({
      id: '@increment',
      date: +Mock.Random.date('T'),
      title: '@title(2, 4)',
      'tag|1': ['CNN', 'LSTM', 'Corp', 'Transform'],
      'status|1': ['published', 'draft', 'deleted']
    }))
  }
  ModelList[i + 101] = tmp
}

module.exports = [
  /*
  {
    url: '/project/execute',
    type: 'post',
    response: _ => {
      return {
        code: 200,
        data: 'success'
      }
    }
  },*/

  {
    url: '/project/list',
    type: 'get',
    response: config => {
      const { importance, type, title, page = 1, limit = 20, sort } = config.query

      let mockList = List.filter(item => {
        if (importance && item.importance !== +importance) return false
        if (type && item.type !== type) return false
        if (title && item.title.indexOf(title) < 0) return false
        return true
      })

      if (sort === '-id') {
        mockList = mockList.reverse()
      }

      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

      return {
        code: 200,
        data: {
          total: mockList.length,
          items: pageList
        }
      }
    }
  },

  {
    url: '/project/detail',
    type: 'get',
    response: config => {
      const { id } = config.query
      for (const project of List) {
        if (project.id === +id) {
          return {
            code: 200,
            data: project
          }
        }
      }
    }
  },

  {
    url: '/project/pv',
    type: 'get',
    response: _ => {
      return {
        code: 200,
        data: {
          pvData: [
            { key: 'PC', pv: 1024 },
            { key: 'mobile', pv: 1024 },
            { key: 'ios', pv: 1024 },
            { key: 'android', pv: 1024 }
          ]
        }
      }
    }
  },

  {
    url: '/project/create',
    type: 'post',
    response: _ => {
      return {
        code: 200,
        data: 'success'
      }
    }
  },

  {
    url: '/project/update',
    type: 'put',
    response: _ => {
      return {
        code: 200,
        data: 'success'
      }
    }
  },

  {
    url: '/project/delete',
    type: 'delete',
    response: _ => {
      return {
        code: 200,
        data: 'success'
      }
    }
  },

  {
    url: '/project/history',
    type: 'get',
    response: config => {
      const items = history.items
      return {
        code: 200,
        data: {
          total: items.length,
          items: items
        }
      }
    }
  },

  {
    url: '/project/model/list',
    type: 'get',
    response: config => {
      const { id } = config.query
      return {
        code: 200,
        data: {
          total: ModelList[id].length,
          items: ModelList[id]
        }
      }
    }
  }

]
