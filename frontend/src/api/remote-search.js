import request from '@/utils/request'

export function searchUser(name) {
  return request({
    url: '/vue-admin-template/search/user',
    method: 'get',
    params: { name }
  })
}

export function transactionList(query) {
  return request({
    url: '/vue-admin-template/transaction/list',
    method: 'get',
    params: query
  })
}

export function searchDataset(name) {
  return request({
    url: '/search/dataset',
    method: 'get',
    params: { name }
  })
}
