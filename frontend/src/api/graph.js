import request from '@/utils/request'

export function fetchGraph(id) {
  return request({
    url: '/graph/detail',
    method: 'get',
    params: { id }
  })
}
