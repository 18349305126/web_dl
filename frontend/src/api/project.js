import request from '@/utils/request'

export function execute(data) {
  return request({
    url: '/project/execute',
    method: 'post',
    data
  })
}

export function save(data) {
  return request({
    url: '/project/save',
    method: 'post',
    data
  })
}

export function fetchList(params) {
  return request({
    url: '/project/list',
    method: 'get',
    params
  })
}

export function fetchProject(id) {
  return request({
    url: '/project/detail',
    method: 'get',
    params: { id }
  })
}

export function fetchPv(pv) {
  return request({
    url: '/project/pv',
    method: 'get',
    params: { pv }
  })
}

export function createProject(data) {
  return request({
    url: '/project/create',
    method: 'post',
    data
  })
}

export function updateProject(data) {
  return request({
    url: '/project/update',
    method: 'put',
    data
  })
}

export function deleteProject(data) {
  return request({
    url: '/project/delete',
    method: 'delete',
    data
  })
}

export function fetchHistory(params) {
  return request({
    url: '/project/history',
    method: 'get',
    params
  })
}

export function fetchModel(id) {
  return request({
    url: '/project/model/list',
    method: 'get',
    params: { id }
  })
}

export function loadModel(id) {
  return request({
    url: '/project/model/detail',
    method: 'get',
    params: { id }
  })
}

export function createModel(data) {
  return request({
    url: '/project/model/create',
    method: 'post',
    data
  })
}

export function deletemodel(data) {
  return request({
    url: '/project/model/delete',
    method: 'delete',
    data
  })
}

export function deleteModel(data) {
  return request({
    url: '/project/model/delete',
    method: 'post',
    data
  })
}
