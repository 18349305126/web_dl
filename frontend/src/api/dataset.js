import request from '@/utils/request'

export function fetchList(params) {
  return request({
    url: '/dataset/list',
    method: 'get',
    params
  })
}

export function fetchDataset(id) {
  return request({
    url: '/dataset/detail',
    method: 'get',
    params: { id }
  })
}

export function fetchPv(pv) {
  return request({
    url: '/dataset/pv',
    method: 'get',
    params: { pv }
  })
}

export function createDataset(data) {
  return request({
    url: '/dataset/create',
    method: 'post',
    data
  })
}

export function updateDataset(data) {
  return request({
    url: '/dataset/update',
    method: 'put',
    data
  })
}

export function deleteDataset(data) {
  return request({
    url: '/dataset/delete',
    method: 'delete',
    data
  })
}

export function mergeFile(data) {
  return request({
    url: '/dataset/mergeFile',
    method: 'post',
    data
  })
}
