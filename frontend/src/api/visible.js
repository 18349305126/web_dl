import request from '@/utils/request'

export function volRender(data) {
    return request({
      url: '/visible/render',
      method: 'post',
      params:data
    })
}

export function volRender2(data) {
  return request({
    url: '/visible/render2',
    method: 'post',
    params:data
  })
}

export function testRender(data) {
    return request({
      url: '/visible/test',
      method: 'post',
      data,
    })
}
